import rasterio
import rasterio.features
import numpy as np
from shapely.geometry import shape, mapping
from shapely.ops import transform as shapely_transform
from pyproj import Transformer
import json
import os
import glob
import time
import csv
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


# ── Configuration ──
elevation_folder = "elevation_data_RF"
output_folder = "flood_geojsons"
water_threshold = 0.1
simplify_tolerance_m = 3        # removes detail smaller than X meters
min_polygon_area_m2 = 2000       # skip polygons smaller than X square meters
rounding_step_cm = 5  # round sea levels to nearest 5 cm


def round_to_step(value_cm, step_cm):
    return round(value_cm / step_cm) * step_cm


def process_tile(tif_path, sea_levels, water_threshold, simplify_tolerance_m=3, min_polygon_area_m2=100, downsample=2):
    """Process one tile for all sea levels. Returns dict of sea_level -> list of polygons."""
    with rasterio.open(tif_path) as dataset:
        if downsample > 1:
            # Read at reduced resolution (e.g. 2x = 1/4 the pixels)
            new_h = max(1, dataset.height // downsample)
            new_w = max(1, dataset.width // downsample)
            elevation = dataset.read(1, out_shape=(new_h, new_w),
                                     resampling=rasterio.enums.Resampling.average)
            # Adjust transform for the new resolution
            tile_transform = dataset.transform * dataset.transform.scale(
                dataset.width / new_w, dataset.height / new_h
            )
        else:
            elevation = dataset.read(1)
            tile_transform = dataset.transform

    min_elev = float(elevation.min())
    max_elev = float(elevation.max())

    # Early exit: if entire tile is below water threshold, nothing to flood
    if max_elev < water_threshold:
        return {}

    # Pre-compute the base mask (pixels above water threshold)
    above_water = elevation >= water_threshold

    results = {}
    prev_polys = None

    for sea_level in sea_levels:
        # Skip if lowest point is already above this sea level
        if min_elev >= sea_level:
            continue

        # If fully flooded, all higher levels produce same result
        if max_elev < sea_level and prev_polys is not None:
            results[sea_level] = prev_polys
            continue

        flood_mask = above_water & (elevation < sea_level)
        if not flood_mask.any():
            continue

        flood_mask_uint8 = flood_mask.astype(np.uint8)
        raw_shapes = list(rasterio.features.shapes(
            flood_mask_uint8,
            mask=flood_mask_uint8,
            transform=tile_transform,
            connectivity=4
        ))

        polys = []
        for geom, _ in raw_shapes:
            poly = shape(geom)
            if poly.area >= min_polygon_area_m2:
                polys.append(poly.simplify(simplify_tolerance_m, preserve_topology=True))

        if polys:
            results[sea_level] = polys
            if max_elev < sea_level:
                prev_polys = polys

    return results


def merge_sea_level(args):
    """Transform polygons for one sea level and build GeoJSON features.
    Skips expensive unary_union — outputs individual polygons directly.
    Designed to run in a separate process."""
    sea_level, polys, min_polygon_area_m2, output_folder = args

    transformer = Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)

    # Bulk transform function
    def transform_fn(x, y):
        lng, lat = transformer.transform(x, y)
        return np.round(lng, 6), np.round(lat, 6)

    # Transform each polygon and build features directly (no union)
    features = []
    skipped_small = 0

    for poly in polys:
        if poly.area < min_polygon_area_m2:
            skipped_small += 1
            continue

        transformed = shapely_transform(transform_fn, poly)
        geom_geojson = mapping(transformed)

        features.append({
            "type": "Feature",
            "properties": {"name": "Roskilde Fjord", "sea_level_rise_m": sea_level},
            "geometry": geom_geojson
        })

    geojson = {"type": "FeatureCollection", "features": features}

    sea_level_cm = round(sea_level * 100)
    output_file = os.path.join(output_folder, f"flood_{sea_level_cm}cm.geojson")

    if HAS_ORJSON:
        with open(output_file, "wb") as f:
            f.write(orjson.dumps(geojson))
    else:
        with open(output_file, "w") as f:
            json.dump(geojson, f)

    file_size_kb = round(os.path.getsize(output_file) / 1024, 1)

    return sea_level, len(polys), len(features), skipped_small, file_size_kb


if __name__ == '__main__':
    absolute_start_time = time.time()

    # --test flag: only process first 3 sea levels for quick iteration
    test_mode = "--test" in sys.argv

    os.makedirs(output_folder, exist_ok=True)

    projections = []
    with open("sea_rise_projections/roskilde_fjord_projections.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            projections.append({
                "scenario": row ["scenario"],
                "year": int(row["year"]),
                "sea_level_cm": float(row["sea_level_cm"])
            })

    print(f"Loaded {len(projections)} projections")

    lookup = {}
    unique_levels_cm = set()

    for p in projections:
        rounded_cm = round_to_step(p["sea_level_cm"], rounding_step_cm)
        key = f"{p['scenario']}_{p['year']}"
        lookup[key] = {
            "scenario": p["scenario"],
            "year": p["year"],
            "exact_cm": p["sea_level_cm"],
            "rounded_cm": rounded_cm,
            "geojson_file": f"flood_{rounded_cm}cm.geojson"
        }
        unique_levels_cm.add(rounded_cm)

    sea_levels = sorted([cm / 100 for cm in unique_levels_cm])

    if test_mode:
        sea_levels = sea_levels[:3]
        print(f"TEST MODE: only processing first 3 sea levels")

    print(f"Unique sea levels after rounding to {rounding_step_cm}cm steps: {len(sea_levels)}")
    print(f"Values (m): {sea_levels}")
    if HAS_ORJSON:
        print("Using orjson for fast serialization")
    else:
        print("orjson not installed, using stdlib json (pip install orjson for ~5x faster writes)")
    print()

    tif_files = glob.glob(os.path.join(elevation_folder, "*.tif"))
    print(f"Found {len(tif_files)} GeoTIFF files")
    print()

    # ── Process all tiles in parallel, each tile handles all sea levels ──
    print(f"Processing tiles with {os.cpu_count()} workers...")
    all_polygons = defaultdict(list)
    completed = 0
    total = len(tif_files)

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {
            executor.submit(process_tile, tif, sea_levels, water_threshold, simplify_tolerance_m, min_polygon_area_m2): tif
            for tif in sorted(tif_files)
        }
        for future in as_completed(futures):
            tif_path = futures[future]
            completed += 1
            try:
                tile_results = future.result()
            except Exception as e:
                print(f"  ERROR processing {os.path.basename(tif_path)}: {e}")
                continue

            levels_hit = list(tile_results.keys())
            if levels_hit:
                for sea_level, polys in tile_results.items():
                    all_polygons[sea_level].extend(polys)
                print(f"  [{completed}/{total}] {os.path.basename(tif_path)}: flooding at {len(levels_hit)} levels")
            else:
                print(f"  [{completed}/{total}] {os.path.basename(tif_path)}: no flooding")

    print(f"\nTile processing complete in {round(time.time() - absolute_start_time, 1)}s")
    print()

    # ── Merge, transform, and save per sea level (parallel) ──
    merge_start = time.time()
    merge_args = []
    for sea_level in sea_levels:
        polys = all_polygons.get(sea_level, [])
        if len(polys) == 0:
            print(f"  No flooding at {sea_level}m. Skipping.")
            continue
        print(f"  Sea level {sea_level}m: {len(polys)} polygons to merge")
        merge_args.append((sea_level, polys, min_polygon_area_m2, output_folder))

    print(f"\nMerging {len(merge_args)} sea levels in parallel with {os.cpu_count()} workers...")

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(merge_sea_level, args): args[0] for args in merge_args}
        for future in as_completed(futures):
            sea_level = futures[future]
            try:
                sl, total_polys, final_count, skipped, file_kb = future.result()
                if file_kb is not None:
                    print(f"  {sl}m: {total_polys} polygons -> {final_count} features "
                          f"(skipped {skipped} small, {file_kb} KB)")
                else:
                    print(f"  {sl}m: unexpected geometry type, skipped")
            except Exception as e:
                print(f"  ERROR merging {sea_level}m: {e}")

    merge_elapsed = round(time.time() - merge_start, 1)
    print(f"\nMerge phase complete in {merge_elapsed}s")
    print()

    # ── Save lookup table for frontend ──
    lookup_file = os.path.join(output_folder, "lookup.json")
    with open(lookup_file, "w") as f:
        json.dump(lookup, f, indent=2)
    print(f"Saved lookup table: {lookup_file}")

    absolute_elapsed = round(time.time() - absolute_start_time, 1)
    print(f"From start to finish it took {absolute_elapsed} seconds!")
    print("Done!")

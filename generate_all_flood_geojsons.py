import rasterio
import rasterio.features
import numpy as np
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from pyproj import Transformer
import json
import os
import glob
import time


# ── Configuration ──
elevation_folder = "elevation_data_RF"
output_folder = "flood_geojsons"
water_threshold = 0.1
sea_levels = [0.5, 1.0, 1.5, 2.0]
simplify_tolerance_m = 20        # removes detail smaller than X meters
min_polygon_area_m2 = 5000       # skip polygons smaller than X square meters

os.makedirs(output_folder, exist_ok=True)

tif_files = glob.glob(os.path.join(elevation_folder, "*.tif"))
print(f"Found {len(tif_files)} GeoTIFF files")
for f in sorted(tif_files):
    print(f"{os.path.basename(f)}")
print()

transformer = Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)

for sea_level in sea_levels:
    start_time = time.time()
    print(f"=== Processing sea level rise: {sea_level}m ===")

    all_polygons = []

    for tif_path in sorted(tif_files):
        filename = os.path.basename(tif_path)

        with rasterio.open(tif_path) as dataset:
            elevation = dataset.read(1)
            transform = dataset.transform

            flood_mask = (elevation >= water_threshold) & (elevation < sea_level)
            pixel_count = np.sum(flood_mask)

            if pixel_count == 0:
                print(f"{filename}: no flooding")
                continue

            print(f" {filename}: {pixel_count:,} flooded pixels")

            flood_mask_uint8 = flood_mask.astype(np.uint8)
            raw_shapes = list(rasterio.features.shapes(
                flood_mask_uint8,
                mask=flood_mask_uint8,
                transform=transform
            ))

            for geom, value in raw_shapes:
                poly = shape(geom) # research further
                if poly.area < 10:
                    continue
                all_polygons.append(poly)

    print(f" Total polygons before merge: {len(all_polygons)}")

    if len(all_polygons) == 0:
        print(f" No flooding at {sea_level}m. Skpping \n")
        continue

    # ── Step 3b: Merge all polygons into one unified shape ──
    merged = unary_union(all_polygons)

    if merged.geom_type == "Polygon":
        merged_list = [merged]
    elif merged.geom_type == "MultiPolygon":
        merged_list = list(merged.geoms)
    else:
        print(f"  Unexpected geometry type: {merged.geom_type}. Skipping.\n")
        continue

    print(f"  Polygons after merge: {len(merged_list)}")

    # ── Step 3c: Filter small polygons, simplify, convert to lat/lng ──
    features = []
    skipped_small = 0

    for polygon in merged_list:
        # Skip tiny polygons (area is in square meters since we're in UTM)
        if polygon.area < min_polygon_area_m2:
            skipped_small += 1
            continue

        # Simplify in UTM (tolerance is in meters now — this actually works!)
        simplified = polygon.simplify(simplify_tolerance_m, preserve_topology=True)

        # Convert exterior ring from UTM to lat/lng
        utm_coords = list(simplified.exterior.coords)
        latlng_coords = []
        for x, y in utm_coords:
            lng, lat = transformer.transform(x, y)
            latlng_coords.append([round(lng, 6), round(lat, 6)])

        # Convert any holes (interior rings) too
        holes = []
        for interior in simplified.interiors:
            hole_coords = []
            for x, y in interior.coords:
                lng, lat = transformer.transform(x, y)
                hole_coords.append([round(lng, 6), round(lat, 6)])
            holes.append(hole_coords)

        coordinates = [latlng_coords] + holes

        feature = {
            "type": "Feature",
            "properties": {
                "name": "Roskilde Fjord",
                "sea_level_rise_m": sea_level
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates
            }
        }
        features.append(feature)

    print(f"  Skipped {skipped_small} small polygons (< {min_polygon_area_m2} sqm)")
    print(f"  Final polygons: {len(features)}")
    
print("Done!")
import rasterio
import rasterio.features
import numpy as np
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from pyproj import Transformer
import json

filepath = "elevation_data_RF/DTM_1km_6175_694.tif"
sea_level_rise = 1
water_threshold = 0.1
output_file = "flood_zone_test_1m.geojson"


with rasterio.open(filepath) as dataset:
    elevation = dataset.read(1)
    transform = dataset.transform
    source_crs = dataset.crs


    flood_mask = (elevation >= water_threshold) & (elevation < sea_level_rise)

    pixel_count = np.sum(flood_mask)
    print(f"Pixels that would flood {pixel_count:,}")
    print(f"That's {round(100 * pixel_count / elevation.size, 2)}% of the tile")

    if pixel_count == 0:
        print("No flooding at this sea level rise. Try a higher value")
        exit()

    
    flood_mask_uint8 = flood_mask.astype(np.uint8)

    raw_shapes = list(rasterio.features.shapes(
        flood_mask_uint8,
        mask = flood_mask_uint8,
        transform=transform
    ))

    print(f"Raw polygons found: {len(raw_shapes)}")


transformer = Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)

converted_features = []

for geom, value in raw_shapes:
    shapely_polygon = shape(geom)

    if shapely_polygon.area < 10:
        continue

    utm_coords = list(shapely_polygon.exterior.coords)
    latlng_coords = []
    for x, y in utm_coords:
        lng, lat = transformer.transform(x, y)
        latlng_coords.append([lng, lat])

    converted_feature = {
        "type": "Feature",
        "properties": {
            "name": "Roskilde Fjord",
            "sea_level_rise_m": sea_level_rise
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [latlng_coords]
        }
    }
    converted_features.append(converted_feature)

print(f"Polygons after filtering tiny ones: {len(converted_features)}")

geojson = {
    "type": "FeatureCollection",
    "features": converted_features
}

with open(output_file, "w") as f:
    json.dump(geojson, f)

file_size_kb = round(len(json.dumps(geojson)) / 1024, 1)
print(f"Saved to {output_file} ({file_size_kb} KB)")
import rasterio
import numpy as np

filepath = "elevation_data_RF/DTM_1km_6175_694.tif"

with rasterio.open(filepath) as dataset:
    elevation = dataset.read(1)

    print("=== Height distribution ===")
    print()

    # Count pixels in narrow bands to see where they cluster
    bands = [
        (-1.0, 0.0),
        (0.0, 0.1),
        (0.1, 0.2),
        (0.2, 0.3),
        (0.3, 0.4),
        (0.4, 0.5),
        (0.5, 1.0),
        (1.0, 2.0),
        (2.0, 5.0),
        (5.0, 10.0),
        (10.0, 25.0),
    ]

    total = elevation.size

    for low, high in bands:
        count = np.sum((elevation >= low) & (elevation < high))
        pct = round(100 * count / total, 1)
        bar = "#" * int(pct)
        print(f"  {low:6.1f}m to {high:5.1f}m : {count:>8,} pixels ({pct:5.1f}%) {bar}")

    print()
    print(f"  Total pixels: {total:,}")

    # Show the 10 most common height values (rounded to 1 decimal)
    rounded = np.round(elevation.flatten(), 1)
    unique, counts = np.unique(rounded, return_counts=True)
    top10_indices = np.argsort(-counts)[:10]

    print()
    print("=== 10 most common heights (rounded to 0.1m) ===")
    for i in top10_indices:
        print(f"  {unique[i]:6.1f}m : {counts[i]:>8,} pixels")
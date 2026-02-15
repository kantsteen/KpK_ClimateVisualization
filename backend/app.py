from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

co2_df=pd.read_csv("data/owid-co2-data.csv")
temp_df=pd.read_csv("data/NASA_GISTEMP.csv", skiprows=1)

# @app.get("/api/co2")
# def get_co2(year: int):
#     df = co2_df[
#         (co2_df["year"] == year) &
#         (co2_df["iso_code"].notna()) &
#         (co2_df["iso_code"].str.len() == 3)
#     ]
    
#     result_df = df[["iso_code", "co2", "co2_per_capita"]].dropna()
#     result_df.columns = ["code", "co2", "co2_per_capita"]
    
#     return result_df.to_dict(orient="records")


# CO2 endpoint

@app.get("/api/co2/all")
def get_co2():
    df = co2_df[
        (co2_df["year"] >= 1950) &
        (co2_df["iso_code"].notna()) &
        (co2_df["iso_code"].str.len() == 3)
    ]

    # filter out huge outliers
    df = df[df["co2_per_capita"] <= 100]
    
    result_df = df[["year", "iso_code", "co2", "co2_per_capita"]].dropna()
    result_df.columns = ["year", "code", "co2", "co2_per_capita"]
        
    return result_df.to_dict(orient="records")


# Temperature endpoint

@app.get("/api/temperature")
def get_temperature():
    df = temp_df[["Year", "J-D"]].copy()
    df = df[df["J-D"] != "***"]
    df.columns = ["year", "temperature"]
    df["temperature"] = df["temperature"].astype(float)
    return df.to_dict(orient="records")




# Flood GeoJSONs endpoint

with open("flood_geojsons/lookup.json") as f:
    flood_lookup = json.load(f)

@app.get("/api/flood-zones")
def get_flood_zones(scenario: str, year: int):
    key = f"{scenario}_{year}"

    if key not in flood_lookup:
        return JSONResponse(
            status_code=404,
            content= {"error": f"No data for {scenario} year {year}"}
        )

    entry = flood_lookup[key]

    geojson_filename = entry["geojson_file"]

    geojson_path = f"flood_geojsons/{geojson_filename}"
    with open(geojson_path) as f:
        geojson_data = json.load(f)
    
    return geojson_data
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

co2_df=pd.read_csv("data/owid-co2-data.csv")
temp_df=pd.read_csv("data/NASA_GISTEMP.csv", skiprows=1)

@app.get("/api/co2")
def get_co2(year: int, metric: str = "total"):
    df = co2_df[
        (co2_df["year"] == year) &
        (co2_df["iso_code"].notna()) &
        (co2_df["iso_code"].str.len() == 3)
    ]
    
    column = "co2" if metric == "total" else "co2_per_capita"
    result_df = df[["iso_code", column]].dropna()
    result_df.columns = ["code", "value"]
        
    return result_df.to_dict(orient="records")


@app.get("/api/temperature")
def get_temperature():
    df = temp_df[["Year", "J-D"]].copy()
    df = df[df["J-D"] != "***"]
    df.columns = ["year", "temperature"]
    df["temperature"] = df["temperature"].astype(float)
    return df.to_dict(orient="records")
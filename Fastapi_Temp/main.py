from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path # Sti-håndtering
from pydantic import BaseModel #FastApi bibliotek
from typing import List #Type hints

# Konfiguration
DATA_DIR = Path(__file__).resolve().parent / "data"
GISTEMP_PATH = DATA_DIR / "gistemp.csv"

BASELINE = "1951-1980"  # GISTEMP anomaly baseline
UNIT = "°C"

# Pydantic output
class YearValue(BaseModel):
    year: int
    value: float

class Meta(BaseModel):
    dataset: str
    baseline: str
    unit: str
    start_year: int
    end_year: int

class HistoricalResponse(BaseModel):
    meta: Meta
    series: List[YearValue]

# App
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_gistemp_annual(path: Path) -> pd.DataFrame:
    """Læs CSV og returnér en DataFrame med to kolonner: year, value (annual anomaly)."""
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")

    df = pd.read_csv(path, low_memory=False)
    cols = set(df.columns)

    # Case 1: NASA wide format: Year + J-D (annual)
    if "Year" in cols and "J-D" in cols:
        out = df[["Year", "J-D"]].copy()
        out.columns = ["year", "value"]

    # Case 2: Tidy: year + value
    elif "year" in cols and "value" in cols:
        out = df[["year", "value"]].copy()

    else:
        raise ValueError("CSV format not recognized. Expected (Year,J-D) or (year,value).")

    # Rens datatyper
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["year", "value"])

    out["year"] = out["year"].astype(int)
    out = out.sort_values("year")

    # Story 8 kræver 1880–present
    out = out[out["year"] >= 1880]

    return out

@app.get("/api/temperature/historical", response_model=HistoricalResponse)
def temperature_historical():
    """Story 8: Annual temperature anomaly timeline (1880–present)."""
    try:
        annual = load_gistemp_annual(GISTEMP_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if annual.empty:
        raise HTTPException(status_code=404, detail="No data found in the requested range (>= 1880).")

    start_year = int(annual["year"].min())
    end_year = int(annual["year"].max())

    return HistoricalResponse(
        meta=Meta(
            dataset="NASA GISTEMP annual temperature anomaly",
            baseline=BASELINE,
            unit=UNIT,
            start_year=start_year,
            end_year=end_year,
        ),
        series=[
            YearValue(year=int(r["year"]), value=float(r["value"]))
            for r in annual.to_dict(orient="records")
        ],
    )

import pandas as pd

# this file is just for testing the functioning and printing its output
co2_df = pd.read_csv("data/owid-co2-data.csv")

def get_co2(year: int, metric: str = "total"):
    df = co2_df[
        (co2_df["year"] == year) &
        (co2_df["iso_code"].notna()) &
        (co2_df["iso_code"].str.len() == 3)
    ]
    
    column = "co2" if metric == "total" else "co2_per_capita"
    result_df = df[["iso_code", column]].dropna()
    result_df.columns = ["code", "value"]
    
    print(result_df)
    
    return result_df.to_dict(orient="records")

get_co2(2020, "total")


temp_df=pd.read_csv("data/NASA_GISTEMP.csv", skiprows=1)

def get_temperature():
    df = temp_df[["Year", "J-D"]].copy()
    df = df[df["J-D"] != "***"]
    df.columns = ["year", "temperature"]
    df["temperature"] = df["temperature"].astype(float)

    print(df)

    return df.to_dict(orient="records")

get_temperature()
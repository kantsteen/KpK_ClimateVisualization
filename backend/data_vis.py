import pandas as pd

# this file is just for testing the functioning and printing its output
co2_df = pd.read_csv("data/owid-co2-data.csv")

def get_co2():
    df = co2_df[
        (co2_df["year"] >= 1950) &
        (co2_df["iso_code"].notna()) &
        (co2_df["iso_code"].str.len() == 3)
    ]
    
    result_df = df[["year", "iso_code", "co2", "co2_per_capita"]].dropna()
    result_df.columns = ["year", "code", "co2", "co2_per_capita"]
    
    print(result_df)
    
    return result_df.to_dict(orient="records")

get_co2()


temp_df=pd.read_csv("data/NASA_GISTEMP.csv", skiprows=1)

def get_temperature():
    df = temp_df[["Year", "J-D"]].copy()
    df = df[df["J-D"] != "***"]
    df.columns = ["year", "temperature"]
    df["temperature"] = df["temperature"].astype(float)

    print(df)

    return df.to_dict(orient="records")

#get_temperature()
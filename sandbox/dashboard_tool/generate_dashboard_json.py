import pandas as pd
import numpy as np
import os

# Files
EDU_FILE = "opri_pivoted.csv"
PROXIMITY_FILE = "DATA/schools_proximity_analysis.csv"

def generate_dashboard_json():
    edu_df = pd.read_csv(EDU_FILE)
    prox_df = pd.read_csv(PROXIMITY_FILE)

    # Aggregate
    prox_summary = prox_df.groupby("country").agg(
        total_schools=("name", "count"),
        hotspot_count=("near_hotspot", lambda x: (x == True).sum())
    )
    prox_summary["hotspot_ratio"] = prox_summary["hotspot_count"] / prox_summary["total_schools"]

    oos_col = "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)"
    pop_p = "School age population, primary education, both sexes (number)"
    pop_s = "School age population, secondary education, both sexes (number)"

    country_edu = edu_df.groupby("COUNTRY_NAME").agg({oos_col: "sum", pop_p: "sum", pop_s: "sum"})
    country_edu["oos_rate"] = (country_edu[oos_col] / (country_edu[pop_p] + country_edu[pop_s])) * 100
    
    # Merge and export
    merged = country_edu.join(prox_summary, how="left").reset_index()
    merged = merged.rename(columns={"COUNTRY_NAME": "country"})
    merged.to_json("dashboard_data.json", orient="records")
    print("dashboard_data.json generated.")

if __name__ == "__main__":
    generate_dashboard_json()

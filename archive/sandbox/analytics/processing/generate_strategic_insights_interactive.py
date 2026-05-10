import pandas as pd
import numpy as np
import os
import sys

# Files
EDU_FILE = "opri_pivoted.csv"
PROXIMITY_FILE = "DATA/schools_proximity_analysis.csv"

def generate_insights_with_weights(oos_weight):
    # oos_weight is 0-100, prox_weight is 100 - oos_weight
    oos_w = oos_weight / 100.0
    prox_w = 1.0 - oos_w

    if not os.path.exists(EDU_FILE) or not os.path.exists(PROXIMITY_FILE):
        return {"error": "Data files missing."}

    edu_df = pd.read_csv(EDU_FILE)
    prox_df = pd.read_csv(PROXIMITY_FILE)

    prox_summary = prox_df.groupby("country").agg(
        total_schools=("name", "count"),
        hotspot_count=("near_hotspot", lambda x: (x == True).sum())
    )
    prox_summary["hotspot_ratio"] = prox_summary["hotspot_count"] / prox_summary["total_schools"]

    oos_col = "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)"
    pop_p = "School age population, primary education, both sexes (number)"
    pop_s = "School age population, secondary education, both sexes (number)"

    country_edu = edu_df.groupby("COUNTRY_NAME").agg({oos_col: "sum", pop_p: "sum", pop_s: "sum"})
    country_edu["total_pop"] = country_edu[pop_p] + country_edu[pop_s]
    country_edu["oos_rate"] = (country_edu[oos_col] / country_edu["total_pop"]) * 100

    merged = country_edu.join(prox_summary, how="left")
    
    results = []
    for country, row in merged.iterrows():
        insufficient_data = np.isnan(row["oos_rate"]) or row["total_schools"] == 0
        
        if insufficient_data:
            insight = "Insufficient Data"
            action = "Urgent: Field-based Data Collection Required"
        else:
            oos_score = min(row["oos_rate"], 100) * oos_w
            prox_score = min(row["hotspot_ratio"] * 100, 100) * prox_w
            total_score = oos_score + prox_score
            
            if total_score > 60:
                insight = f"Critical Risk (Score: {total_score:.1f})"
                action = "Immediate Infrastructure & Security Intervention"
            elif total_score > 30:
                insight = f"Elevated Risk (Score: {total_score:.1f})"
                action = "Attendance Support & Conflict-Sensitive Programming"
            else:
                insight = "Low Risk / Stable"
                action = "Monitor"
        
        results.append({
            "Country": country,
            "Key Insight": insight,
            "Pressing Need/Action": action
        })
        
    return results

if __name__ == "__main__":
    # Allow weight passed as CLI argument
    weight = float(sys.argv[1]) if len(sys.argv) > 1 else 50.0
    data = generate_insights_with_weights(weight)
    pd.DataFrame(data).to_csv("country_strategic_insights_interactive.csv", index=False)
    print("Success: Updated with weight", weight)

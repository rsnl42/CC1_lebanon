import pandas as pd
import numpy as np
import os

# Files
EDU_FILE = "opri_pivoted.csv"
PROXIMITY_FILE = "DATA/schools_proximity_analysis.csv"

def generate_enhanced_insights():
    if not os.path.exists(EDU_FILE) or not os.path.exists(PROXIMITY_FILE):
        print("Data files missing.")
        return

    edu_df = pd.read_csv(EDU_FILE)
    prox_df = pd.read_csv(PROXIMITY_FILE)

    # Aggregate proximity data to country level
    prox_summary = prox_df.groupby("country").agg(
        total_schools=("name", "count"),
        hotspot_count=("near_hotspot", lambda x: (x == True).sum())
    )
    prox_summary["hotspot_ratio"] = prox_summary["hotspot_count"] / prox_summary["total_schools"]

    # Calculate country-level education metrics
    oos_col = "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)"
    pop_p = "School age population, primary education, both sexes (number)"
    pop_s = "School age population, secondary education, both sexes (number)"

    country_edu = edu_df.groupby("COUNTRY_NAME").agg({oos_col: "sum", pop_p: "sum", pop_s: "sum"})
    country_edu["total_pop"] = country_edu[pop_p] + country_edu[pop_s]
    country_edu["oos_rate"] = (country_edu[oos_col] / country_edu["total_pop"]) * 100

    # Merge
    merged = country_edu.join(prox_summary, how="left")
    
    data = []
    for country, row in merged.iterrows():
        # Identify Data Insufficiency
        insufficient_data = np.isnan(row["oos_rate"]) or row["total_schools"] == 0
        
        if insufficient_data:
            insight = "Insufficient Data"
            reasoning_insight = "Enrollment or school proximity data is missing or incomplete for this region."
            action = "Urgent: Field-based Data Collection Required"
            reasoning_action = "Global datasets are incomplete; manual field assessment is needed to determine risk levels."
        else:
            # Multi-dimensional scoring (0-100)
            oos_score = min(row["oos_rate"], 100) * 0.5
            prox_score = min(row["hotspot_ratio"] * 100, 100) * 0.5
            total_score = oos_score + prox_score
            
            if total_score > 60:
                insight = f"Critical Risk (Score: {total_score:.1f})"
                action = "Immediate Infrastructure & Security Intervention"
                reasoning_action = "High OOS rates combined with proximity to conflict hotspots indicate urgent need for protection."
            elif total_score > 30:
                insight = f"Elevated Risk (Score: {total_score:.1f})"
                action = "Attendance Support & Conflict-Sensitive Programming"
                reasoning_action = "Moderate risk levels suggest localized vulnerabilities; program adaptation is recommended."
            else:
                insight = "Low Risk / Stable"
                action = "Monitor"
                reasoning_action = "Stable metrics observed."
            
            reasoning_insight = f"Score derived from OOS Rate ({row['oos_rate']:.1f}%) and School Proximity Ratio ({row['hotspot_ratio']:.2f})."
        
        data.append({
            "Country": country,
            "Key Insight": insight,
            "Reasoning (Insight)": reasoning_insight,
            "Pressing Need/Action": action,
            "Reasoning (Action)": reasoning_action
        })
        
    pd.DataFrame(data).to_csv("country_strategic_insights_v2.csv", index=False)
    print("Success: country_strategic_insights_v2.csv generated.")

if __name__ == "__main__":
    generate_enhanced_insights()

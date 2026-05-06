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

    # Load vulnerability count data
    vuln_stats = pd.read_csv("school_vulnerability_count.csv")
    # Get latest year per country
    latest_vuln = vuln_stats.sort_values("year").groupby("country").tail(1)
    latest_vuln = latest_vuln.set_index("country")

    # Keep OOS calculation for insight text, but use vulnerability percentage for Marker/Risk Logic
    oos_col = "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)"
    pop_p = "School age population, primary education, both sexes (number)"
    pop_s = "School age population, secondary education, both sexes (number)"

    country_edu = edu_df.groupby("COUNTRY_NAME").agg({oos_col: "sum", pop_p: "sum", pop_s: "sum"})
    country_edu["total_pop"] = country_edu[pop_p] + country_edu[pop_s]
    country_edu["oos_rate"] = (country_edu[oos_col] / country_edu["total_pop"]) * 100

    # Merge
    merged = country_edu.join(latest_vuln, how="left")
    
    # Standardize names
    mapping = {
        "Lao People's Democratic Republic": "Laos",
        "Syrian Arab Republic": "Syria",
        "United Republic of Tanzania": "Tanzania",
        "Venezuela (Bolivarian Republic of)": "Venezuela",
        "Viet Nam": "Vietnam",
        "Democratic Republic of the Congo": "DR Congo",
        "Central African Republic": "CAR"
    }
    merged.index = merged.index.map(lambda x: mapping.get(x, x))
    
    data = []
    for country, row in merged.iterrows():
        # Use vulnerability percentage for risk markers
        vuln_pct = row["vulnerable_percentage"]
        
        insight = "Insufficient Vulnerability Data"
        reasoning_insight = "Conflict proximity data is unavailable for this country."
        action = "Monitor"
        reasoning_action = "Data collection required."
        
        if np.isnan(vuln_pct):
            pass
        elif vuln_pct > 60:
            insight = f"Critical Risk: {vuln_pct:.1f}% Vulnerability"
            action = "Immediate Infrastructure & Security Intervention"
            reasoning_action = f"High percentage ({vuln_pct:.1f}%) of schools within 50km of conflict hotspots."
        elif vuln_pct > 30:
            insight = f"Elevated Risk: {vuln_pct:.1f}% Vulnerability"
            action = "Attendance Support & Conflict-Sensitive Programming"
            reasoning_action = f"Moderate percentage ({vuln_pct:.1f}%) of schools near conflict."
        else:
            insight = f"Low Risk / Stable: {vuln_pct:.1f}% Vulnerability"
            action = "Standard Monitoring"
            reasoning_action = "Low proportion of schools affected by conflict hotspots."
            
        data.append({
            "Country": country,
            "Key Insight": insight,
            "Reasoning (Insight)": reasoning_insight,
            "Pressing Need/Action": action,
            "Reasoning (Action)": reasoning_action
        })
        
    pd.DataFrame(data).to_csv("country_strategic_insights_v2.csv", index=False)
    print("Success: country_strategic_insights_v2.csv generated with updated marker logic.")

if __name__ == "__main__":
    generate_enhanced_insights()

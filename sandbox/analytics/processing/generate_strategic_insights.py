import pandas as pd
import os

# Files
EDU_FILE = "opri_pivoted.csv"
VULN_FILE = "timeline_map/data/schools_vulnerability.csv"
CONFLICT_FILE = "timeline_map/data/country_yearly_conflict.csv"

def generate_insights():
    if not os.path.exists(EDU_FILE):
        print("Data file missing.")
        return

    edu_df = pd.read_csv(EDU_FILE)
    countries = edu_df["COUNTRY_NAME"].unique()
    
    # Placeholder lists
    data = []
    
    for country in countries:
        c_edu = edu_df[edu_df["COUNTRY_NAME"] == country]
        
        # Calculate key metrics
        oos_col = "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)"
        pop_p = "School age population, primary education, both sexes (number)"
        pop_s = "School age population, secondary education, both sexes (number)"
        
        total_pop = c_edu[pop_p].sum() + c_edu[pop_s].sum()
        total_oos = c_edu[oos_col].sum()
        rate = (total_oos / total_pop * 100) if total_pop > 0 else 0
        
        # Determine insight and action
        insight = "Stable"
        reasoning_insight = "Data shows consistent enrollment trends."
        action = "Monitor"
        reasoning_action = "Standard monitoring recommended."
        
        if rate > 30:
            insight = f"High Out-of-School Rate: {rate:.2f}%"
            reasoning_insight = f"Calculated OOS rate exceeds 30% threshold based on primary/secondary population data."
            action = "Targeted Scholarships & Infrastructure"
            reasoning_action = "High OOS rates often correlate with economic exclusion; financial support can bridge the access gap."
        elif rate > 15:
            insight = f"Moderate Risk: {rate:.2f}% OOS"
            reasoning_insight = f"OOS rate is elevated."
            action = "Attendance Support & Hybrid Monitoring"
            reasoning_action = "Early intervention at this stage can prevent further dropouts."
            
        data.append({
            "Country": country,
            "Key Insight": insight,
            "Reasoning (Insight)": reasoning_insight,
            "Pressing Need/Action": action,
            "Reasoning (Action)": reasoning_action
        })
        
    pd.DataFrame(data).to_csv("country_strategic_insights.csv", index=False)
    print("Success: country_strategic_insights.csv generated.")

if __name__ == "__main__":
    generate_insights()

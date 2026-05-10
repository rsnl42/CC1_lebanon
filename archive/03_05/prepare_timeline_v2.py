
import pandas as pd
import os

# Files
EDU_FILE = "opri_pivoted.csv"
CONFLICT_FILE = "timeline_map/data/country_yearly_conflict.csv"
OUTPUT_FILE = "timeline_map_v2/data/country_yearly_enriched.csv"

def enrich_timeline_data():
    print("Loading datasets...")
    df_edu = pd.read_csv(EDU_FILE)
    df_conflict = pd.read_csv(CONFLICT_FILE)
    
    # Calculate OOS Rate %
    pop_p_col = "School age population, primary education, both sexes (number)"
    pop_s_col = "School age population, secondary education, both sexes (number)"
    oos_ps_col = "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)"
    
    df_edu["Total_Pop"] = df_edu[pop_p_col].fillna(0) + df_edu[pop_s_col].fillna(0)
    df_edu["OOS_Rate"] = (df_edu[oos_ps_col] / df_edu["Total_Pop"]) * 100
    
    # Clean up naming
    df_edu = df_edu.rename(columns={"COUNTRY_NAME": "Country", "YEAR": "Year"})
    edu_subset = df_edu[["Country", "Year", "OOS_Rate"]]
    
    # Merge with conflict
    print("Merging data...")
    enriched = pd.merge(df_conflict, edu_subset, on=["Country", "Year"], how="left")
    
    # Handle NaNs for OOS_Rate (keep as null for the map logic)
    
    print(f"Saving to {OUTPUT_FILE}...")
    enriched.to_csv(OUTPUT_FILE, index=False)
    print("Success!")

if __name__ == "__main__":
    enrich_timeline_data()

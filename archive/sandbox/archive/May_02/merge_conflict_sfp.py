import pandas as pd
import os

# Paths
HRP1_PATH = "DATA/HRP_1_countries_geocoded.csv"
HRP2_PATH = "DATA/HRP_2_countries_geocoded.csv"
SFP_LEVEL_PATH = "DATA/2021 Global Survey of School Meal Programs - Data for Dissemination/Survey Data - Excel Format/country_level.xlsx"
SFP_COVERAGE_PATH = "DATA/2021 Global Survey of School Meal Programs - Data for Dissemination/Survey Data - Excel Format/country_coverage.xlsx"
OUTPUT_PATH = "May_02/conflict_sfp_merged.csv"

def normalize_country(name):
    if pd.isna(name): return name
    name = str(name).strip()
    mapping = {
        "Palestine": "State of Palestine",
        "Syria": "Syrian Arab Republic",
        "Democratic Republic of Congo": "Democratic Republic of the Congo",
        "DRC": "Democratic Republic of the Congo",
        "Venezuela": "Venezuela (Bolivarian Republic of)",
        "Vietnam": "Viet Nam",
        "Tanzania": "United Republic of Tanzania",
        "Bolivia": "Bolivia (Plurinational State of)",
        "Russia": "Russian Federation",
        "South Korea": "Republic of Korea",
        "North Korea": "Democratic People's Republic of Korea"
    }
    return mapping.get(name, name)

print("Loading and aggregating conflict data...")
hrp1 = pd.read_csv(HRP1_PATH)
hrp2 = pd.read_csv(HRP2_PATH)
conflict = pd.concat([hrp1, hrp2])

# Aggregate fatalities and events by country
conflict_agg = conflict.groupby('Country').agg({
    'Fatalities': 'sum',
    'Events': 'sum'
}).reset_index()
conflict_agg['Country'] = conflict_agg['Country'].apply(normalize_country)
conflict_agg.rename(columns={'Country': 'country_name'}, inplace=True)

print("Loading School Meal Survey data...")
# Load country level data (qualitative/attendance)
sfp_level = pd.read_excel(SFP_LEVEL_PATH)
sfp_level_cols = [
    'Country (short name)', 
    'World Bank income group', 
    'Is student attendance recorded?', 
    'Can individual students who received school feeding be linked to attendance?',
    'Describe impacts of school feeding on students',
    'Did your country have a national school feeding program?'
]
sfp_level = sfp_level[sfp_level_cols]
sfp_level['Country (short name)'] = sfp_level['Country (short name)'].apply(normalize_country)
sfp_level.rename(columns={'Country (short name)': 'country_name'}, inplace=True)

# Load coverage data (quantitative)
sfp_coverage = pd.read_excel(SFP_COVERAGE_PATH)
sfp_coverage['country'] = sfp_coverage['country'].apply(normalize_country)
sfp_coverage.rename(columns={'country': 'country_name'}, inplace=True)

print("Merging datasets...")
# First merge SFP datasets
sfp_combined = pd.merge(sfp_level, sfp_coverage, on='country_name', how='outer')

# Then merge with conflict data
merged = pd.merge(sfp_combined, conflict_agg, on='country_name', how='left')

# Fill NaN fatalities for non-conflict countries if they aren't in HRP list (optional, but here we keep them as NaN to distinguish HRP vs non-HRP)
# merged['Fatalities'] = merged['Fatalities'].fillna(0)

# Save output
merged.to_csv(OUTPUT_PATH, index=False)
print(f"Success! Merged data saved to {OUTPUT_PATH}")

# Quick summary for the console
conflict_zones = merged[merged['Fatalities'] > 0]
print(f"\nSummary of Conflict Zones ({len(conflict_zones)} countries identified):")
print(conflict_zones[['country_name', 'Fatalities', 'pct_coverage', 'Can individual students who received school feeding be linked to attendance?']].head(10))

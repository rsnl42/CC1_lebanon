import pandas as pd
import os

# Paths
MERGED_DATA_PATH = "May_02/conflict_sfp_merged.csv"
SFP_PROGRAM_LEVEL_PATH = "DATA/2021 Global Survey of School Meal Programs - Data for Dissemination/Survey Data - Excel Format/country_program_level.xlsx"
SFP_COVERAGE_PATH = "DATA/2021 Global Survey of School Meal Programs - Data for Dissemination/Survey Data - Excel Format/country_coverage.xlsx"
OUTPUT_FOLDER = "May_02"

# Load merged data to get conflict countries
merged_df = pd.read_csv(MERGED_DATA_PATH)
conflict_countries = merged_df[merged_df['Fatalities'] > 0]['country_name'].tolist()

print(f"Loaded {len(conflict_countries)} conflict countries.")

# Load SFP program level data
sfp_program_df = pd.read_excel(SFP_PROGRAM_LEVEL_PATH)

# Normalize country names in SFP program data for merging
def normalize_country_program(name):
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
        "North Korea": "Democratic People's Republic of Korea",
        "Yemen": "Yemen" # Added Yemen based on previous context
    }
    return mapping.get(name, name)

# Corrected column name for country in sfp_program_df
sfp_program_df['country_name'] = sfp_program_df['Country'].apply(normalize_country_program)

print(f"Loaded SFP program data with {len(sfp_program_df)} entries.")

# Load SFP coverage data and normalize country names
sfp_coverage = pd.read_excel(SFP_COVERAGE_PATH)
sfp_coverage['country_name'] = sfp_coverage['country'].apply(normalize_country_program)


# Filter SFP program data for conflict countries
sfp_conflict_program = sfp_program_df[sfp_program_df['country_name'].isin(conflict_countries)].copy()

print(f"Filtered {len(sfp_conflict_program)} program entries for conflict countries.")

# Analyze funding information
funding_cols = [
    'country_name',
    'Program name',
    'Money spent on this SFP in the most recently completed school year',
    'Currency used for money spent on this SFP',
    'Contribution: National program implementer',
    'Contribution: Nongovernmental program implementer',
    'Contribution: Subnational government',
    "Contribution: Students' families and community'",
    'Contribution: Private sector',
    'Contribution: Other',
    'Contribution: Other, specify',
    'Was funding for this SFP part of the national budget?'
]

# Ensure all funding columns exist before selecting
funding_cols_exist = [col for col in funding_cols if col in sfp_conflict_program.columns]
sfp_funding_analysis = sfp_conflict_program[funding_cols_exist]

print("--- Funding Analysis for Conflict Countries ---")
print(sfp_funding_analysis.head().to_string())

# Save the analysis to CSV
output_file = os.path.join(OUTPUT_FOLDER, "conflict_sfp_funding_analysis.csv")
sfp_funding_analysis.to_csv(output_file, index=False)
print(f"Funding analysis saved to {output_file}")

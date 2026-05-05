import pandas as pd
import os
import json

# Paths
AGG_FILES = [
    'almost_FINAL/analysis/HRP_1_countries_geocoded_yearly_admin_agg.csv',
    'almost_FINAL/analysis/HRP_2_countries_geocoded_yearly_admin_agg.csv'
]
GEO_FILES = [
    'almost_FINAL/DATA/HRP_1_countries_geocoded.csv',
    'almost_FINAL/DATA/HRP_2_countries_geocoded.csv'
]
SCHOOLS_FILE = 'DATA/schools_combined.csv'
OUTPUT_DIR = 'timeline_map/data'

def prepare_data():
    print("Loading aggregated conflict data...")
    df_agg = pd.concat([pd.read_csv(f) for f in AGG_FILES])
    
    print("Loading coordinate data...")
    df_geo_list = []
    for f in GEO_FILES:
        # Only load necessary columns to save memory
        df_geo_list.append(pd.read_csv(f, usecols=['Country', 'Admin2', 'Latitude', 'Longitude']))
    
    df_coords = pd.concat(df_geo_list).drop_duplicates(subset=['Country', 'Admin2'])
    df_coords = df_coords.dropna(subset=['Latitude', 'Longitude'])

    print("Merging conflict data with coordinates...")
    df_conflict = pd.merge(df_agg, df_coords, on=['Country', 'Admin2'], how='inner')
    
    # Filter out rows with 0 events and fatalities to reduce size
    df_conflict = df_conflict[(df_conflict['Events'] > 0) | (df_conflict['Fatalities'] > 0)]
    
    # Save processed conflict data
    conflict_output = os.path.join(OUTPUT_DIR, 'conflict_data.csv')
    df_conflict.to_csv(conflict_output, index=False)
    print(f"Saved conflict data to {conflict_output}")

    print("Loading school data...")
    # Read schools, only keeping necessary columns
    df_schools = pd.read_csv(SCHOOLS_FILE, usecols=['name', 'latitude', 'longitude'])
    df_schools = df_schools.dropna(subset=['latitude', 'longitude'])
    
    # Sample schools if they are too many (optional, but 100k is a lot for a web map without tiling)
    # The user didn't ask to sample, so let's try to keep them all first.
    # But for a "shareable URL", large files are bad.
    # Let's see how big the CSV is.
    
    schools_output = os.path.join(OUTPUT_DIR, 'schools_data.csv')
    df_schools.to_csv(schools_output, index=False)
    print(f"Saved school data to {schools_output}")

if __name__ == "__main__":
    prepare_data()

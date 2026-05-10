import pandas as pd
import os
import json

# Paths
AGG_FILES = [
    'almost_FINAL/analysis/HRP_1_countries_geocoded_yearly_admin_agg.csv',
    'almost_FINAL/analysis/HRP_2_countries_geocoded_yearly_admin_agg.csv'
]
OUTPUT_DIR = 'timeline_map/data'

def prepare_choropleth_data():
    print("Loading aggregated conflict data...")
    df_agg = pd.concat([pd.read_csv(f) for f in AGG_FILES])
    
    # Group by Country and Year for Choropleth
    # We sum up Admin-level events to Country-level
    df_country_year = df_agg.groupby(['Country', 'Year'])[['Events', 'Fatalities']].sum().reset_index()
    
    # Normalize naming for common GeoJSON mismatches if known, 
    # but for now we'll stick to the CSV names.
    
    output_path = os.path.join(OUTPUT_DIR, 'country_yearly_conflict.csv')
    df_country_year.to_csv(output_path, index=False)
    print(f"Saved country-level data to {output_path}")

if __name__ == "__main__":
    prepare_choropleth_data()

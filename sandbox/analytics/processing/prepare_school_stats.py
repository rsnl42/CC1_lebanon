import pandas as pd
import os

# Using the proximity analysis file which has hotspot info
SCHOOLS_FILE = 'DATA/schools_proximity_analysis.csv'
OUTPUT_DIR = 'timeline_map/data'

def prepare_school_data():
    print("Loading school proximity data...")
    # Read schools, keeping necessary columns
    df_schools = pd.read_csv(SCHOOLS_FILE, usecols=['name', 'latitude', 'longitude', 'country', 'near_hotspot', 'hotspot_info'])
    df_schools = df_schools.dropna(subset=['latitude', 'longitude'])
    
    # Save the cleaned school data
    schools_output = os.path.join(OUTPUT_DIR, 'schools_data.csv')
    df_schools.to_csv(schools_output, index=False)
    print(f"Saved school data to {schools_output}")
    
    # Pre-calculate country-level stats
    stats = df_schools.groupby('country').agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'name': 'count'
    }).reset_index()
    stats.columns = ['country', 'lat', 'lon', 'count']
    
    stats_output = os.path.join(OUTPUT_DIR, 'school_stats.csv')
    stats.to_csv(stats_output, index=False)
    print(f"Saved school stats to {stats_output}")

if __name__ == "__main__":
    prepare_school_data()

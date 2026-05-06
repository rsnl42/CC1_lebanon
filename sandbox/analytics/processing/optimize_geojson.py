
import json
import pandas as pd
import os

GEOJSON_FILE = 'timeline_map/data/countries.geojson'
CONFLICT_FILE = 'timeline_map/data/country_yearly_conflict.csv'
OUTPUT_FILE = 'timeline_map/data/countries_optimized.geojson'

def optimize_geojson():
    print(f"Loading conflict data to identify relevant countries...")
    conflict_df = pd.read_csv(CONFLICT_FILE)
    
    # Normalize country names to match common variations
    relevant_countries = set(conflict_df['Country'].unique())
    # Add common variations or manual overrides if necessary
    relevant_countries.add("Democratic Republic of the Congo")
    relevant_countries.add("Congo")
    relevant_countries.add("Syria")
    relevant_countries.add("Palestine")
    
    print(f"Found {len(relevant_countries)} relevant countries.")

    print(f"Loading original GeoJSON (14MB)...")
    with open(GEOJSON_FILE, 'r') as f:
        data = json.load(f)

    original_count = len(data['features'])
    print(f"Original GeoJSON has {original_count} features.")

    filtered_features = []
    
    for feature in data['features']:
        name = feature['properties'].get('name')
        iso3 = feature['properties'].get('ISO3166-1-Alpha-3')
        
        # Check if country is relevant
        is_relevant = False
        if name in relevant_countries:
            is_relevant = True
        elif iso3 in ["COD", "SYR", "PSE", "LBN", "MLI", "MMR", "NGA", "SSD", "SDN", "YEM", "MOZ", "HTI", "VEN", "NER"]:
            is_relevant = True
            
        if is_relevant:
            # Round coordinates to 5 decimal places (~1.1m precision) to save space
            feature['geometry']['coordinates'] = recursive_round(feature['geometry']['coordinates'], 5)
            filtered_features.append(feature)

    data['features'] = filtered_features
    print(f"Filtered to {len(filtered_features)} features.")

    print(f"Saving optimized GeoJSON...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, separators=(',', ':')) # Compact JSON

    original_size = os.path.getsize(GEOJSON_FILE) / (1024 * 1024)
    new_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"Original Size: {original_size:.2f} MB")
    print(f"Optimized Size: {new_size:.2f} MB")
    print(f"Reduction: {((original_size - new_size) / original_size) * 100:.2f}%")

def recursive_round(coords, precision):
    if isinstance(coords, (int, float)):
        return round(float(coords), precision)
    return [recursive_round(c, precision) for c in coords]

if __name__ == "__main__":
    optimize_geojson()

import pandas as pd
import numpy as np
import os

def merge_schools():
    print("Loading school data...")
    path1 = 'DATA/school_data/schools_merged.csv'
    path2 = 'DATA/school_data_hdx/schools_all.csv'
    
    if not os.path.exists(path1) or not os.path.exists(path2):
        print(f"Error: One or more source files missing.")
        return

    df1 = pd.read_csv(path1)
    df2 = pd.read_csv(path2)
    
    print(f"Dataset 1: {len(df1)} schools")
    print(f"Dataset 2: {len(df2)} schools")

    # Standardize columns: merge all unique columns from both
    all_cols = list(set(df1.columns) | set(df2.columns))
    for col in all_cols:
        if col not in df1.columns: df1[col] = np.nan
        if col not in df2.columns: df2[col] = np.nan
        
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Calculate "detail score" (number of non-null columns)
    # We prioritize records with more information
    df['detail_score'] = df.notnull().sum(axis=1)
    
    # Sort by detail score so we keep the most detailed one when dropping duplicates
    df = df.sort_values(by='detail_score', ascending=False)
    
    print(f"Total schools before merging: {len(df)}")
    
    # Simple duplicate detection based on name and rounded coordinates
    # Rounding to 4 decimal places is roughly 11 meters at the equator, 
    # which is a safe threshold for "same location" for schools.
    df['lat_round'] = df['latitude'].round(4)
    df['lon_round'] = df['longitude'].round(4)
    df['name_clean'] = df['name'].fillna('').str.lower().str.strip()
    
    # Step 1: Drop duplicates where name and rounded location match
    df_clean = df.drop_duplicates(subset=['name_clean', 'lat_round', 'lon_round'], keep='first')
    
    # Step 2: Drop duplicates where ONLY location matches very closely
    # This catches schools that might be named slightly differently or have missing names in one source
    df_final = df_clean.drop_duplicates(subset=['lat_round', 'lon_round'], keep='first')
    
    print(f"Total schools after deduplication: {len(df_final)}")
    
    # Cleanup helper columns
    df_final = df_final.drop(columns=['detail_score', 'lat_round', 'lon_round', 'name_clean'])
    
    output_path = 'DATA/schools_combined.csv'
    df_final.to_csv(output_path, index=False)
    print(f"Saved combined school data to {output_path}")

if __name__ == "__main__":
    merge_schools()

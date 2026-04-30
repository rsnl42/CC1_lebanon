import pandas as pd
import os

# --- Configuration ---
INPUT_DIR = "DATA/HRP_1_countries_geocoded/"
OUTPUT_FILE = "DATA/HRP_1_countries_geocoded.csv"

def merge_hrp_csvs():
    print(f"--- Starting merge process for files in: {INPUT_DIR} ---")
    
    # List all files in the input directory
    try:
        all_files = os.listdir(INPUT_DIR)
        csv_files = [f for f in all_files if f.endswith('.csv')]
        csv_files.sort() # Ensure consistent order
    except FileNotFoundError:
        print(f"Error: Directory not found - {INPUT_DIR}")
        return

    if not csv_files:
        print("No CSV files found to merge.")
        return

    print(f"Found {len(csv_files)} files to merge.")

    dataframes = []
    total_rows = 0

    for filename in csv_files:
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            # Read the CSV file. Use latin1 encoding as seen in previous geocoding scripts.
            df = pd.read_csv(filepath, encoding='latin1')
            dataframes.append(df)
            rows = len(df)
            total_rows += rows
            print(f"  - Merged: {filename} ({rows:,} rows)")
        except Exception as e:
            print(f"  - Error reading {filename}: {e}")

    if not dataframes:
        print("No valid data was merged.")
        return

    # Concatenate all DataFrames
    print("\nConcatenating data...")
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Save to the output CSV file
    print(f"Saving merged data to: {OUTPUT_FILE}")
    try:
        merged_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n--- Merge Complete! ---")
        print(f"Total rows in merged file: {len(merged_df):,}")
    except Exception as e:
        print(f"Error saving merged file: {e}")

if __name__ == "__main__":
    merge_hrp_csvs()

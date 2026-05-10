import pandas as pd
import os

INPUT_FILE = "opri_filtered.csv"
OUTPUT_FILE = "opri_pivoted.csv"

def pivot_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Reading {INPUT_FILE}...")
    # Using low_memory=False to handle mixed types
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print(f"Cleaning data...")
    # Drop rows with missing values in key columns
    df = df.dropna(subset=["COUNTRY_NAME", "YEAR", "INDICATOR_NAME", "VALUE"])
    
    # Ensure numeric types
    df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype(int)

    # Some indicators might have duplicate entries for the same country/year/indicator
    # due to minor variations in other columns. We aggregate by taking the mean (usually just one value exists).
    print("Pivoting data (this may take a moment)...")
    pivot_df = df.pivot_table(
        index=["COUNTRY_NAME", "COUNTRY_ID", "YEAR"],
        columns="INDICATOR_NAME",
        values="VALUE",
        aggfunc="first"  # Use 'first' to keep the original value as it's usually unique
    )

    # Flatten the multi-index columns and reset index
    pivot_df = pivot_df.reset_index()

    # Drop columns that are entirely NaN (just in case)
    pivot_df = pivot_df.dropna(axis=1, how="all")

    print(f"Saving to {OUTPUT_FILE}...")
    pivot_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"Success! Pivoted data has {pivot_df.shape[0]} rows and {pivot_df.shape[1]} columns.")
    print("\nTop 5 rows preview:")
    print(pivot_df.head())

if __name__ == "__main__":
    pivot_data()

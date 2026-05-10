import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os # For path joining, though not strictly necessary if files are in root

# --- Configuration ---
INPUT_CSV_FILE = 'opri_pivoted.csv'
OUTPUT_PNG_FILE = 'correlation_heatmap.png'
IDENTIFIER_COLUMNS = ['COUNTRY_NAME', 'COUNTRY_ID', 'YEAR'] # Columns to exclude from correlation calculation
COUNTRY_SELECTION_PERCENTILE = 0.20 # Select top 20% of countries
YEAR_SELECTION_PERCENTILE = 0.20 # Select top 20% of years

# --- Helper Function for Completeness ---
def calculate_row_completeness(row, feature_columns):
    """
    Calculates the proportion of non-null and non-zero values for a given row
    across specified feature columns.
    """
    relevant_data = row[feature_columns]
    # Check for not null AND not zero
    non_null_non_zero_mask = relevant_data.apply(lambda x: pd.notna(x) and x != 0)
    return non_null_non_zero_mask.sum() / len(feature_columns)

# --- Main Script Logic ---
def generate_heatmap():
    """
    Loads data, filters it based on completeness, calculates correlation matrix,
    and generates a clustered heatmap.
    """
    print(f"Loading data from: {INPUT_CSV_FILE}")
    try:
        df = pd.read_csv(INPUT_CSV_FILE)
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_CSV_FILE}' not found. Please ensure it is in the correct directory.")
        return # Exit function if file not found
    except Exception as e:
        print(f"Error loading CSV file '{INPUT_CSV_FILE}': {e}")
        return

    # --- Identify Feature Columns ---
    # Select all numeric columns first
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    # Exclude identifier columns from the feature set
    feature_cols = [col for col in numeric_cols if col not in IDENTIFIER_COLUMNS]

    if not feature_cols:
        print("Error: No numeric feature columns found for correlation analysis after excluding identifiers.")
        return

    # --- Data Filtering ---
    print("Calculating data completeness...")
    # Calculate row-wise completeness
    df['row_completeness'] = df.apply(
        calculate_row_completeness,
        axis=1,
        feature_columns=feature_cols
    )

    # Filter countries based on average row completeness
    country_completeness = df.groupby('COUNTRY_NAME')['row_completeness'].mean()
    # Ensure at least one country is selected, even if percentile results in 0
    num_countries_to_select = max(1, int(len(country_completeness) * COUNTRY_SELECTION_PERCENTILE))
    top_countries = country_completeness.nlargest(num_countries_to_select).index.tolist()
    print(f"Selected top {len(top_countries)} countries based on completeness.")

    # Filter years based on average row completeness
    year_completeness = df.groupby('YEAR')['row_completeness'].mean()
    # Ensure at least one year is selected
    num_years_to_select = max(1, int(len(year_completeness) * YEAR_SELECTION_PERCENTILE))
    top_years = year_completeness.nlargest(num_years_to_select).index.tolist()
    print(f"Selected top {len(top_years)} years based on completeness.")

    # Apply filtering to the DataFrame
    filtered_df = df[
        df['COUNTRY_NAME'].isin(top_countries) &
        df['YEAR'].isin(top_years)
    ].copy() # Use .copy() to prevent SettingWithCopyWarning

    if filtered_df.empty:
        print("Error: No data remaining after filtering. This might be due to very strict thresholds or insufficient data.")
        return

    # Re-confirm feature columns for the filtered data.
    # This is important if some columns became all-null/all-zero after filtering,
    # though .corr() handles this by default by dropping them.
    # We'll just ensure we select from the filtered data's numeric columns.
    filtered_numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
    filtered_feature_cols = [col for col in filtered_numeric_cols if col not in IDENTIFIER_COLUMNS]

    if not filtered_feature_cols:
        print("Error: No numeric feature columns found in the filtered data after re-evaluation.")
        return
    
    # --- Correlation Matrix Calculation ---
    print("Calculating correlation matrix for filtered data...")
    correlation_matrix = filtered_df[filtered_feature_cols].corr()

    # Drop columns/rows that might have NaNs due to correlation calculation on sparse data
    # (e.g., if a feature had no variance after filtering)
    correlation_matrix = correlation_matrix.dropna(axis=0, how='all').dropna(axis=1, how='all')

    if correlation_matrix.empty:
        print("Error: Correlation matrix is empty after calculation. This might happen if filtered data has no variance in any feature.")
        return

    # --- Clustered Heatmap Visualization ---
    print(f"Generating clustered heatmap and saving to {OUTPUT_PNG_FILE}...")
    
    # Use seaborn.clustermap to create the heatmap with hierarchical clustering
    # 'method' and 'metric' for clustering, 'cmap' for color scheme.
    # 'standard_scale=0' or '1' can be used to scale rows/columns if needed, 
    # but for correlation matrix, it's usually not necessary.
    g = sns.clustermap(
        correlation_matrix,
        method='average',     # Linkage method for clustering
        metric='euclidean',   # Distance metric for clustering
        cmap='viridis',       # Colormap for the heatmap
        linewidths=.5,        # Lines between cells
        figsize=(14, 14),     # Figure size for better readability
        cbar_pos=(.02, .8, .03, .15) # Position of the color bar (optional fine-tuning)
    )

    # Ensure the plot is saved correctly
    # Using bbox_inches='tight' to prevent labels from being cut off.
    # dpi for resolution.
    plt.savefig(OUTPUT_PNG_FILE, dpi=300, bbox_inches='tight')
    print(f"Clustered heatmap successfully saved to {OUTPUT_PNG_FILE}")

if __name__ == "__main__":
    generate_heatmap()

import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson # Not used here, but good to keep if extending
import os
import numpy as np
import matplotlib.colors as mcolors

# --- Configuration ---
CSV_DIR = 'DATA/PWD_100m_sub_national_CSV/'
OUTPUT_DIR = 'April_30/'
LAT_COL = 'pwc_lat'
LON_COL = 'pwc_lon'
VALUE_COL = 'pwd_m'
NUM_CATEGORIES = 5
COLOR_SCHEME_NAME = "PWD_Density_Scheme" # Custom name for the colormap

# --- Ensure output directory exists ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Define a sequential color map ---
# Using a perceptually uniform colormap like viridis, or a custom one
# Define 5 distinct colors for the 5 categories.
custom_colors = ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c'] # Example: YlGnBu-like
# Get hex colors for each category
category_hex_colors = [mcolors.to_hex(color) for color in custom_colors]


# --- Function to create map for a single CSV ---
def create_pwd_map(csv_file_path, output_html_path):
    try:
        df = pd.read_csv(csv_file_path, encoding='latin1')
        df.columns = df.columns.str.lower() # Lowercase columns

        # Check if required columns exist
        if not all(col in df.columns for col in [LAT_COL, LON_COL, VALUE_COL]):
            print(f"Error: Missing one or more required columns ({LAT_COL}, {LON_COL}, {VALUE_COL}) in {csv_file_path}. Skipping file.")
            return

        # Convert critical columns to numeric, coercing errors to NaN
        df[LAT_COL] = pd.to_numeric(df[LAT_COL], errors='coerce')
        df[LON_COL] = pd.to_numeric(df[LON_COL], errors='coerce')
        df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors='coerce')

        # Drop rows with NaN in critical columns
        df.dropna(subset=[LAT_COL, LON_COL, VALUE_COL], inplace=True)

        if df.empty:
            print(f"No valid data found in {csv_file_path} after cleaning. Skipping.")
            return

        # --- Categorize PWD_M values ---
        # Use qcut for N quantile bins if possible. If not enough unique values, fall back.
        actual_num_categories = 0
        try:
            # Attempt to create NUM_CATEGORIES quantile bins
            df['pwd_m_category'] = pd.qcut(df[VALUE_COL], q=NUM_CATEGORIES, labels=False, duplicates='drop')
            actual_num_categories = df['pwd_m_category'].nunique()
            if actual_num_categories < NUM_CATEGORIES:
                print(f"Warning: Only {actual_num_categories} unique categories created for {VALUE_COL} in {csv_file_path} using qcut. Adjusting legend.")
        except ValueError as ve:
            print(f"Warning: Could not create {NUM_CATEGORIES} quantiles for {VALUE_COL} in {csv_file_path} (Error: {ve}). Attempting fixed-width bins.")
            # Fallback to pd.cut if qcut fails
            try:
                df['pwd_m_category'] = pd.cut(df[VALUE_COL], bins=NUM_CATEGORIES, labels=False, duplicates='drop')
                actual_num_categories = df['pwd_m_category'].nunique()
                if actual_num_categories < NUM_CATEGORIES:
                    print(f"Warning: Only {actual_num_categories} unique categories created for {VALUE_COL} in {csv_file_path} using cut. Adjusting legend.")
            except ValueError as ve_cut:
                print(f"Error: Could not create bins for {VALUE_COL} in {csv_file_path} (Error: {ve_cut}). Skipping file.")
                return
        
        # If after both attempts, no categories are created, skip the file
        if actual_num_categories == 0:
            print(f"Error: No categories could be created for {VALUE_COL} in {csv_file_path}. Skipping file.")
            return

        # --- Map categories to colors ---
        # Ensure we only use as many colors as there are actual categories
        current_category_colors = {i: category_hex_colors[i % len(category_hex_colors)] for i in range(actual_num_categories)}
        df['color'] = df['pwd_m_category'].map(current_category_colors)

        # --- Create Folium map ---
        map_center = [df[LAT_COL].mean(), df[LON_COL].mean()]
        m = folium.Map(location=map_center, zoom_start=4, tiles='CartoDB positron')

        # --- Add markers to the map ---
        marker_group = folium.FeatureGroup(name="Population Density Points")
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row[LAT_COL], row[LON_COL]],
                radius=3, # Small, consistent radius
                color=row['color'],
                fill=True,
                fill_color=row['color'],
                fill_opacity=0.7,
                tooltip=f"Lat: {row[LAT_COL]:.4f}, Lon: {row[LON_COL]:.4f}<br>{VALUE_COL.upper()}: {row[VALUE_COL]:.2f}<br>Category: {row['pwd_m_category']}"
            ).add_to(marker_group)
        marker_group.add_to(m)

        # --- Add Legend ---
        generic_legend_labels = ["Very Low", "Low", "Medium", "High", "Very High"]

        display_legend_labels = []
        display_legend_colors = []
        # Iterate up to the actual number of categories
        for i in range(actual_num_categories):
            # Map the integer category index (0 to actual_num_categories-1) to a label and color
            if i < len(generic_legend_labels):
                display_legend_labels.append(generic_legend_labels[i])
            else:
                display_legend_labels.append(f"Category {i+1}") # Fallback label
            display_legend_colors.append(current_category_colors[i])

        legend_html = """
            <div style="position: fixed;
                        bottom: 50px; left: 50px; width: auto; height: auto;
                        border: 2px solid grey; border-radius: 5px; z-index:9999;
                        background-color: rgba(255, 255, 255, 0.8);
                        padding: 10px; font-size: 12px;
                        ">
              <b>Population Weighted Density (Global)</b> <br>
        """
        for label, color in zip(display_legend_labels, display_legend_colors):
            legend_html += f'<i style="background:{color}; width: 14px; height: 14px; display: inline-block; margin-right: 5px; border-radius: 3px;"></i> {label}<br>'
        legend_html += "</div>"

        m.get_root().html.add_child(folium.Element(legend_html))

        # Save map
        m.save(output_html_path)
        print(f"Map generated for {os.path.basename(csv_file_path)} -> {output_html_path}")

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}. Skipping.")
    except Exception as e:
        print(f"An unexpected error occurred while processing {csv_file_path}: {e}")

# --- Main execution loop ---
print(f"Starting script execution to generate maps in '{OUTPUT_DIR}'...")
print(f"Reading PWD CSVs from '{CSV_DIR}'...")

# Get list of CSV files in the specified directory that start with 'PWD_'
try:
    all_files = os.listdir(CSV_DIR)
    csv_files = [f for f in all_files if f.endswith('.csv') and f.startswith('PWD_')]
    csv_files.sort() # Sort by year for consistent output filenames

    if not csv_files:
        print(f"No CSV files starting with 'PWD_' found in {CSV_DIR}.")
    else:
        for csv_file in csv_files:
            csv_full_path = os.path.join(CSV_DIR, csv_file)
            file_base_name = os.path.splitext(csv_file)[0] # e.g., 'PWD_2020_sub_national_100m'
            output_filename = f"{file_base_name}_map.html"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            create_pwd_map(csv_full_path, output_path)

        print("All map generation processes completed.")

except FileNotFoundError:
    print(f"Error: The directory '{CSV_DIR}' was not found. Please ensure it exists.")
except Exception as e:
    print(f"An error occurred during file listing or initial processing: {e}")

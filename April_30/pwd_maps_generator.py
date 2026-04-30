import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os
import numpy as np
import matplotlib.cm as cm # Reverted to standard import
import matplotlib.colors as mcolors
import json
import re # For escaping special characters

# --- Configuration ---
CSV_DIR = 'DATA/PWD_100m_sub_national_CSV/'
OUTPUT_DIR = 'April_30/'
LAT_COL = 'pwc_lat'
LON_COL = 'pwc_lon'
VALUE_COL = 'pwd_m'
COUNTRY_COL = 'country_n'
PLACE_COL = 'adm_n'
POP_COL = 'pop'
AREA_COL = 'area'

NUM_CATEGORIES = 5

# --- Ensure output directory exists ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Define Viridis Color Palette ---
def get_viridis_colors(n):
    cmap = cm.get_cmap('viridis', n) # Using standard cm.get_cmap
    return [mcolors.to_hex(cmap(i)) for i in range(n)]

category_hex_colors = get_viridis_colors(NUM_CATEGORIES)

# --- Function to escape strings for JavaScript tooltips ---
def escape_js_string(text):
    if pd.isna(text):
        return "N/A"
    text = str(text)
    # Escape backslashes, double quotes, and single quotes
    text = text.replace('', '').replace('"', '"').replace("'", "'")
    return text

# --- Function to create map for a single CSV ---
def create_pwd_map(csv_file_path, output_html_path):
    try:
        df = pd.read_csv(csv_file_path, encoding='latin1')
        df.columns = df.columns.str.lower()

        required_cols = [LAT_COL, LON_COL, VALUE_COL, COUNTRY_COL, PLACE_COL, POP_COL, AREA_COL]
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"Error: Missing columns {missing} in {csv_file_path}. Skipping.")
            return

        for col in [LAT_COL, LON_COL, VALUE_COL, POP_COL, AREA_COL]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=[LAT_COL, LON_COL, VALUE_COL], inplace=True)

        if df.empty:
            print(f"No valid data in {csv_file_path}. Skipping.")
            return

        try:
            df['pwd_m_category'] = pd.qcut(df[VALUE_COL], q=NUM_CATEGORIES, labels=False, duplicates='drop')
        except ValueError:
            df['pwd_m_category'] = pd.cut(df[VALUE_COL], bins=NUM_CATEGORIES, labels=False)
        
        actual_num_categories = df['pwd_m_category'].nunique()
        
        current_category_colors = {i: category_hex_colors[i % len(category_hex_colors)] for i in range(actual_num_categories)}
        df['color'] = df['pwd_m_category'].map(current_category_colors)

        # --- Create Folium map ---
        m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')

        # --- Use MarkerCluster for performance ---
        marker_cluster = MarkerCluster(name="Population Weighted Density Clusters").add_to(m)

        for _, row in df.iterrows():
            pop_val = row[POP_COL]
            area_val = row[AREA_COL]
            pwd_val = row[VALUE_COL]
            
            pop_fmt = f"{int(pop_val):,}" if pd.notna(pop_val) else "N/A"
            area_fmt = f"{area_val:,.2f}" if pd.notna(area_val) else "N/A"
            pwd_fmt = f"{pwd_val:,.2f}"

            tooltip_text = (
                f"<b>Country:</b> {escape_js_string(row[COUNTRY_COL])}<br>"
                f"<b>Place:</b> {escape_js_string(row[PLACE_COL])}<br>"
                f"<b>Population:</b> {pop_fmt}<br>"
                f"<b>Area:</b> {area_fmt}<br>"
                f"<b>Population Weighted Density (Median):</b> {pwd_fmt}"
            )

            folium.CircleMarker(
                location=[row[LAT_COL], row[LON_COL]],
                radius=6,
                color=row['color'],
                fill=True,
                fill_color=row['color'],
                fill_opacity=0.8,
                tooltip=tooltip_text
            ).add_to(marker_cluster)

        # --- Add Legend ---
        generic_legend_labels = ["Very Low", "Low", "Medium", "High", "Very High"]
        
        legend_html = f"""
             <div style="position: fixed; 
                         bottom: 50px; left: 50px; width: auto; height: auto; 
                         border:2px solid grey; z-index:9999; font-size:14px;
                         background-color:rgba(255, 255, 255, 0.9);
                         padding: 10px; border-radius: 5px;
                         ">
             <b>Population Weighted Density (Global)</b><br>
        """
        for i in range(actual_num_categories):
            label = generic_legend_labels[i] if i < len(generic_legend_labels) else f"Category {i+1}"
            color = current_category_colors[i]
            legend_html += f'<i style="background:{color}; width: 14px; height: 14px; display: inline-block; margin-right: 5px; border-radius: 3px;"></i> {label}<br>'
        legend_html += "</div>"

        m.get_root().html.add_child(folium.Element(legend_html))
        m.get_root().title = "Population Weighted Density Map: Global"

        m.save(output_html_path)
        print(f"Map generated for {os.path.basename(csv_file_path)} -> {output_html_path}")

    except Exception as e:
        print(f"Error processing {csv_file_path}: {e}")

# --- Main execution loop ---
print(f"Starting script execution to generate maps in '{OUTPUT_DIR}'...")

try:
    all_files = os.listdir(CSV_DIR)
    csv_files = [f for f in all_files if f.endswith('.csv') and f.startswith('PWD_')]
    csv_files.sort()

    for csv_file in csv_files:
        create_pwd_map(os.path.join(CSV_DIR, csv_file), os.path.join(OUTPUT_DIR, f"{os.path.splitext(csv_file)[0]}_map.html"))

    print("All map generation processes completed.")

except Exception as e:
    print(f"An error occurred: {e}")

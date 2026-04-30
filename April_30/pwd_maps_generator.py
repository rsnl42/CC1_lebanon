import pandas as pd
import folium
import os
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors

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
    import matplotlib.pyplot as plt
    cmap = plt.get_cmap('viridis', n)
    return [mcolors.to_hex(cmap(i)) for i in range(n)]

category_hex_colors = get_viridis_colors(NUM_CATEGORIES)

# --- Function to create map for a single CSV ---
def create_pwd_map(csv_file_path, output_html_path):
    try:
        df = pd.read_csv(csv_file_path, encoding='latin1')
        df.columns = df.columns.str.lower() # Lowercase columns

        required_cols = [LAT_COL, LON_COL, VALUE_COL, COUNTRY_COL, PLACE_COL, POP_COL, AREA_COL]
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"Error: Missing columns {missing} in {csv_file_path}. Skipping file.")
            return

        # Convert critical columns to numeric
        for col in [LAT_COL, LON_COL, VALUE_COL, POP_COL, AREA_COL]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with NaN in critical columns
        df.dropna(subset=[LAT_COL, LON_COL, VALUE_COL], inplace=True)

        if df.empty:
            print(f"No valid data found in {csv_file_path} after cleaning. Skipping.")
            return

        # --- Categorize PWD_M values ---
        try:
            df['pwd_m_category'] = pd.qcut(df[VALUE_COL], q=NUM_CATEGORIES, labels=False, duplicates='drop')
        except ValueError:
            df['pwd_m_category'] = pd.cut(df[VALUE_COL], bins=NUM_CATEGORIES, labels=False, duplicates='drop')
        
        actual_num_categories = df['pwd_m_category'].nunique()
        
        # --- Map categories to colors ---
        current_category_colors = {i: category_hex_colors[i] for i in range(actual_num_categories)}
        df['color'] = df['pwd_m_category'].map(current_category_colors)

        # --- Create Folium map ---
        map_center = [df[LAT_COL].mean(), df[LON_COL].mean()]
        m = folium.Map(location=map_center, zoom_start=4, tiles='CartoDB positron')

        # --- Add markers to the map ---
        marker_group = folium.FeatureGroup(name="Population Density Points")
        for _, row in df.iterrows():
            # Format numbers for hover labels
            pop_fmt = f"{int(row[POP_COL]):,}" if not np.isnan(row[POP_COL]) else "N/A"
            area_fmt = f"{row[AREA_COL]:,.2f}" if not np.isnan(row[AREA_COL]) else "N/A"
            pwd_fmt = f"{row[VALUE_COL]:,.2f}"

            tooltip_text = (
                f"<b>Country:</b> {row[COUNTRY_COL]}<br>"
                f"<b>Place:</b> {row[PLACE_COL]}<br>"
                f"<b>Population:</b> {pop_fmt}<br>"
                f"<b>Area:</b> {area_fmt}<br>"
                f"<b>Population Weighted Density (Median):</b> {pwd_fmt}"
            )

            folium.CircleMarker(
                location=[row[LAT_COL], row[LON_COL]],
                radius=4,
                color=row['color'],
                fill=True,
                fill_color=row['color'],
                fill_opacity=0.7,
                tooltip=tooltip_text
            ).add_to(marker_group)
        marker_group.add_to(m)

        # --- Add Legend ---
        generic_legend_labels = ["Very Low", "Low", "Medium", "High", "Very High"]
        
        legend_html = f"""
            <div style="position: fixed;
                        bottom: 50px; left: 50px; width: auto; height: auto;
                        border: 2px solid grey; border-radius: 5px; z-index:9999;
                        background-color: rgba(255, 255, 255, 0.9);
                        padding: 10px; font-size: 12px;
                        ">
              <b>Population Weighted Density (Global)</b> <br>
        """
        for i in range(actual_num_categories):
            label = generic_legend_labels[i] if i < len(generic_legend_labels) else f"Category {i+1}"
            color = current_category_colors[i]
            legend_html += f'<i style="background:{color}; width: 14px; height: 14px; display: inline-block; margin-right: 5px; border-radius: 3px;"></i> {label}<br>'
        legend_html += "</div>"

        m.get_root().html.add_child(folium.Element(legend_html))

        # --- Save with Full HTML Structure ---
        m.save(output_html_path)
        
        # Inject the title into the head after saving
        with open(output_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title_tag = "<title>Population Weighted Density Map: Global</title>"
        if "<title>" in content:
            # Replace existing title if any
            import re
            content = re.sub(r'<title>.*?</title>', title_tag, content)
        else:
            # Insert after <head>
            content = content.replace('<head>', f'<head>\n    {title_tag}')
            
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Map generated for {os.path.basename(csv_file_path)} -> {output_html_path}")

    except Exception as e:
        print(f"An unexpected error occurred while processing {csv_file_path}: {e}")

# --- Main execution loop ---
print(f"Starting script execution to generate maps in '{OUTPUT_DIR}'...")

try:
    all_files = os.listdir(CSV_DIR)
    csv_files = [f for f in all_files if f.endswith('.csv') and f.startswith('PWD_')]
    csv_files.sort()

    if not csv_files:
        print(f"No CSV files starting with 'PWD_' found in {CSV_DIR}.")
    else:
        for csv_file in csv_files:
            csv_full_path = os.path.join(CSV_DIR, csv_file)
            file_base_name = os.path.splitext(csv_file)[0]
            output_filename = f"{file_base_name}_map.html"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            create_pwd_map(csv_full_path, output_path)

        print("All map generation processes completed.")

except Exception as e:
    print(f"An error occurred: {e}")

import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import re

# --- Configuration ---
CSV_DIR = 'DATA/PWD_100m_sub_national_CSV/'
OUTPUT_DIR = '30_04/'  # New directory as requested
MAP_FILES_SUBDIR = 'maps/'  # Subdirectory within 30_04/ to store individual maps
VIEWER_HTML_FILE = 'viewer.html'

# --- Ensure output directories exist ---
os.makedirs(os.path.join(OUTPUT_DIR, MAP_FILES_SUBDIR), exist_ok=True)

# --- Constants ---
LAT_COL = 'pwc_lat'
LON_COL = 'pwc_lon'
VALUE_COL = 'pwd_m'
COUNTRY_COL = 'country_n'
PLACE_COL = 'adm_n'
POP_COL = 'pop'
AREA_COL = 'area'

NUM_CATEGORIES = 5
MAP_TITLE = "Population Weighted Density : Global"
DEFAULT_YEAR = '2020'

# --- Color Palette ---
def get_viridis_colors(n):
    try:
        # Use matplotlib.colormaps directly if available, otherwise fallback to older get_cmap
        if hasattr(cm, 'get_cmap'):
            cmap = cm.get_cmap('viridis', n)
        else:
            cmap = cm.get_cmap('viridis', n)
        return [mcolors.to_hex(cmap(i)) for i in range(n)]
    except Exception as e:
        print(f"Error getting viridis colormap: {e}. Falling back to default.")
        # Fallback if viridis is not available or causes issues
        return ['#edf8fb', '#b2e2e2', '#66c2a4', '#2ca25f', '#006d2c']

# --- Helper functions ---
def escape_js_string(text):
    if pd.isna(text): return "N/A"
    text = str(text)
    # Properly escape characters for JavaScript string literals
    text = text.replace('', '').replace('"', '"').replace("'", "'")
    return text

def format_number(num):
    if pd.isna(num): return "N/A"
    try:
        # Format with commas for thousands separator, and 2 decimal places if float
        if isinstance(num, float):
            return f"{num:,.2f}"
        return f"{int(num):,}"
    except ValueError:
        return str(num) # Fallback if not a number

# --- Function to create a single map HTML ---
def create_individual_map(csv_file_path, output_html_path, year_str):
    print(f"Processing {csv_file_path} for year {year_str}...")
    try:
        df = pd.read_csv(csv_file_path, encoding='latin1')
        df.columns = df.columns.str.lower()

        required_cols = [LAT_COL, LON_COL, VALUE_COL, COUNTRY_COL, PLACE_COL, POP_COL, AREA_COL]
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"Error: Missing columns {missing} in {csv_file_path}. Skipping map generation for {year_str}.")
            return False

        for col in [LAT_COL, LON_COL, VALUE_COL, POP_COL, AREA_COL]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(subset=[LAT_COL, LON_COL, VALUE_COL], inplace=True)

        if df.empty:
            print(f"No valid data found in {csv_file_path}. Skipping map generation for {year_str}.")
            return False

        # Categorize data
        try:
            # Use qcut for quantile-based categorization if possible
            df['pwd_m_category'] = pd.qcut(df[VALUE_COL], q=NUM_CATEGORIES, labels=False, duplicates='drop')
        except ValueError:
            # Fallback to cut if qcut fails (e.g., not enough unique values)
            print(f"qcut failed for {year_str}, falling back to pd.cut.")
            df['pwd_m_category'] = pd.cut(df[VALUE_COL], bins=NUM_CATEGORIES, labels=False)
        
        actual_num_categories = df['pwd_m_category'].nunique()
        
        # Assign colors based on category, ensure enough colors are available
        current_category_colors_list = category_hex_colors[:actual_num_categories]
        current_category_colors = {i: current_category_colors_list[i] for i in range(actual_num_categories)}
        df['color'] = df['pwd_m_category'].map(current_category_colors)

        # --- Create Folium map ---
        m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap', 
                       # Add title to the map container if possible (Folium doesn't directly support this well for static HTML)
                       # The title will be set in the generated HTML later.
                      )

        # --- Use MarkerCluster for performance ---
        marker_cluster = MarkerCluster(name="Population Weighted Density Clusters", 
                                       disableClusteringAtZoom=10, # Adjust zoom level for when to stop clustering
                                       maxClusterRadius=50 # Adjust cluster radius
                                      ).add_to(m)

        # --- Add markers ---
        for _, row in df.iterrows():
            pop_val = row[POP_COL]
            area_val = row[AREA_COL]
            pwd_val = row[VALUE_COL]
            
            pop_fmt = format_number(pop_val)
            area_fmt = format_number(area_val)
            pwd_fmt = format_number(pwd_val)

            # Tooltip text with HTML formatting
            # Note: Dynamic background opacity for tooltips is complex with standard folium.
            # This will use the point color, but not dynamically set opacity for the tooltip box itself.
            tooltip_html = f"""
                <div style="font-family: sans-serif; font-size: 12px; padding: 5px;">
                    <b>Country:</b> {escape_js_string(row[COUNTRY_COL])}<br>
                    <b>Place:</b> {escape_js_string(row[PLACE_COL])}<br>
                    <b>Population:</b> {pop_fmt}<br>
                    <b>Area:</b> {area_fmt}<br>
                    <b>Population Weighted Density (Median):</b> {pwd_fmt}
                </div>
            """
            
            folium.CircleMarker(
                location=[row[LAT_COL], row[LON_COL]],
                radius=6,
                color=row['color'],
                fill=True,
                fill_color=row['color'],
                fill_opacity=0.8,
                tooltip=folium.Tooltip(tooltip_html, sticky=True, opacity=0.9) # sticky=True keeps tooltip open on hover
            ).add_to(marker_cluster)

        # --- Add Legend ---
        generic_legend_labels = ["Very Low", "Low", "Medium", "High", "Very High"]
        
        legend_html_content = f"""
             <div style="position: fixed; 
                         bottom: 50px; left: 50px; width: auto; height: auto; 
                         border:2px solid grey; z-index:9999; font-size:12px;
                         background-color:rgba(255, 255, 255, 0.9);
                         padding: 10px; border-radius: 5px;
                         ">
             <b>{MAP_TITLE}</b><br>
             <b>Population Weighted Density (Median)</b><br>
        """
        # Add color swatches and labels for each category
        for i in range(actual_num_categories):
            label = generic_legend_labels[i] if i < len(generic_legend_labels) else f"Category {i+1}"
            color = current_category_colors[i]
            legend_html_content += f'<i style="background:{color}; width: 14px; height: 14px; display: inline-block; margin-right: 5px; border-radius: 3px; vertical-align: middle;"></i> {label}<br>'
        legend_html_content += "</div>"

        # Add the custom HTML legend to the map
        m.add_child(folium.Element(legend_html_content))
        
        # Set map title (this might not be directly visible in the generated HTML itself, but good practice)
        m.get_root().html.add_child(folium.Element(f"<title>{MAP_TITLE} - {year_str}</title>"))

        m.save(output_html_path)
        print(f"Map generated successfully: {output_html_path}")
        return True

    except Exception as e:
        print(f"Error processing {csv_file_path} for {year_str}: {e}")
        return False

# --- Function to generate the viewer HTML ---
def generate_viewer_html(years, default_year, map_subdir, viewer_filename):
    years_sorted_desc = sorted(years, reverse=True)
    default_map_filename = f"{map_subdir}PWD_{default_year}_sub_national_100m_map.html"

    # Basic HTML structure for the viewer
    viewer_html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{MAP_TITLE}</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ width: 95%; margin: 20px auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: #333; margin-bottom: 10px; }}
        .controls {{ text-align: center; margin-bottom: 20px; }}
        label {{ margin-right: 10px; font-weight: bold; }}
        select, button {{ padding: 10px; margin: 5px; border: 1px solid #ccc; border-radius: 4px; }}
        #map-frame {{ width: 100%; height: 600px; border: 1px solid #ccc; border-radius: 4px; }}
        .limitations {{ font-size: 0.9em; color: #666; margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{MAP_TITLE}</h1>
        <div class="controls">
            <label for="year-select">Select Year:</label>
            <select id="year-select">
                {''.join([f'<option value="{year}" {"selected" if year == default_year else ""}>{year}</option>' for year in years_sorted_desc])}
            </select>
        </div>
        
        <iframe id="map-frame" src="{default_map_filename}"></iframe>
        
        <div class="limitations">
            <p><strong>Note on Advanced Features:</strong></p>
            <ul>
                <li>The map toggling by year is functional.</li>
                <li><strong>Category Filtering:</strong> Direct checkboxes on the legend to filter points by category (e.g., 'Very Low', 'Low') are not natively supported by Folium for dynamically switching point visibility within these pre-generated maps. This would require custom JavaScript to manage marker visibility.</li>
                <li><strong>Tooltip Styling:</strong> Dynamically setting the background opacity of hover labels based on category color is complex and not directly supported by Folium's default tooltips.</li>
            </ul>
        </div>
    </div>

    <script>
        const yearSelect = document.getElementById('year-select');
        const mapFrame = document.getElementById('map-frame');
        const mapBaseName = 'PWD_';
        const mapExtension = '_sub_national_100m_map.html';
        const mapSubDir = '{map_subdir}'; // Relative path to map files

        yearSelect.addEventListener('change', (event) => {{
            const selectedYear = event.target.value;
            const mapFileName = `${{mapBaseName}}${{selectedYear}}${{mapExtension}}`;
            mapFrame.src = mapSubDir + mapFileName;
        }});
    </script>
</body>
</html>
"""
    return viewer_html_content

# --- Main execution ---
if __name__ == "__main__":
    print(f"Starting map generation and viewer script in '{OUTPUT_DIR}'...")

    # Get list of CSV files and extract years
    all_files = os.listdir(CSV_DIR)
    csv_files_info = []
    for f in all_files:
        if f.startswith('PWD_') and f.endswith('.csv'):
            try:
                year_str = f.replace('PWD_', '').replace('_sub_national_100m.csv', '')
                # Basic check to ensure it's a year-like string
                if len(year_str) == 4 and year_str.isdigit():
                    csv_files_info.append({'year': year_str, 'path': os.path.join(CSV_DIR, f)})
            except Exception as e:
                print(f"Could not parse year from filename {f}: {e}")

    # Sort by year in descending order for default and dropdown order
    csv_files_info.sort(key=lambda x: x['year'], reverse=True)
    
    available_years = [info['year'] for info in csv_files_info]

    generated_maps_count = 0
    # Generate individual maps
    for info in csv_files_info:
        year = info['year']
        csv_path = info['path']
        output_map_filename = f"PWD_{year}_sub_national_100m_map.html"
        output_map_path = os.path.join(OUTPUT_DIR, MAP_FILES_SUBDIR, output_map_filename)
        
        if create_individual_map(csv_path, output_map_path, year):
            generated_maps_count += 1

    if generated_maps_count > 0:
        # Generate the viewer HTML if at least one map was created
        print(f"Generating viewer HTML: {os.path.join(OUTPUT_DIR, VIEWER_HTML_FILE)}...")
        viewer_content = generate_viewer_html(available_years, DEFAULT_YEAR, MAP_FILES_SUBDIR, VIEWER_HTML_FILE)
        with open(os.path.join(OUTPUT_DIR, VIEWER_HTML_FILE), 'w', encoding='utf-8') as f:
            f.write(viewer_content)
        print(f"Viewer HTML generated successfully: {os.path.join(OUTPUT_DIR, VIEWER_HTML_FILE)}")
        print("
--- Execution Summary ---")
        print(f"Generated {generated_maps_count} individual map(s) in '{os.path.join(OUTPUT_DIR, MAP_FILES_SUBDIR)}'.")
        print(f"Generated main viewer file: '{os.path.join(OUTPUT_DIR, VIEWER_HTML_FILE)}'.")
        print("
To view the maps:")
        print(f"1. Open the file '{os.path.join(OUTPUT_DIR, VIEWER_HTML_FILE)}' in your web browser.")
        print("   (e.g., if you are in the /workspaces/CC1_lebanon/ directory, you can use: file:///workspaces/CC1_lebanon/30_04/viewer.html)")
        print("2. Use the dropdown to select a year and toggle between the maps.")
        print("
Limitations regarding advanced filtering and tooltip styling have been noted in the viewer file.")
    else:
        print("No maps were generated. Please check CSV files and required columns.")

    print("Script execution finished.")

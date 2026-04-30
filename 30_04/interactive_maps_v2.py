import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import json

# --- Configuration ---
CSV_DIR = 'DATA/PWD_100m_sub_national_CSV/'
OUTPUT_DIR = '30_04/'
MAP_FILES_SUBDIR = 'maps/'
VIEWER_HTML_FILE = 'viewer.html'

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
CATEGORIES = ["Very Low", "Low", "Medium", "High", "Very High"]

def get_viridis_colors(n):
    cmap = cm.get_cmap('viridis', n)
    return [mcolors.to_hex(cmap(i)) for i in range(n)]

def get_rgba_color(hex_color, opacity=0.5):
    rgb = mcolors.to_rgb(hex_color)
    return f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, {opacity})"

def escape_js_string(text):
    if pd.isna(text): return "N/A"
    return str(text).replace("'", "\\'")

def format_number(num):
    if pd.isna(num): return "N/A"
    try:
        return f"{num:,.2f}" if isinstance(num, float) else f"{int(num):,}"
    except:
        return str(num)

def create_advanced_map(csv_file_path, output_html_path, year_str):
    print(f"Creating advanced map for {year_str}...")
    try:
        df = pd.read_csv(csv_file_path, encoding='latin1')
        df.columns = df.columns.str.lower()
        
        cols = [LAT_COL, LON_COL, VALUE_COL, COUNTRY_COL, PLACE_COL, POP_COL, AREA_COL]
        df = df.dropna(subset=[LAT_COL, LON_COL, VALUE_COL])
        for col in [LAT_COL, LON_COL, VALUE_COL, POP_COL, AREA_COL]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Categorize
        try:
            df['cat_idx'] = pd.qcut(df[VALUE_COL], q=NUM_CATEGORIES, labels=False, duplicates='drop')
        except:
            df['cat_idx'] = pd.cut(df[VALUE_COL], bins=NUM_CATEGORIES, labels=False)
        
        actual_n = df['cat_idx'].nunique()
        colors = get_viridis_colors(actual_n)
        
        m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
        
        # Add Title to Map
        title_html = f'<h3 align="center" style="font-size:16px"><b>{MAP_TITLE} ({year_str})</b></h3>'
        m.get_root().html.add_child(folium.Element(title_html))

        # Groups for filtering
        groups = []
        for i in range(actual_n):
            group_name = CATEGORIES[i] if i < len(CATEGORIES) else f"Category {i+1}"
            group = folium.FeatureGroup(name=group_name)
            groups.append(group)

        for _, row in df.iterrows():
            c_idx = int(row['cat_idx'])
            hex_color = colors[c_idx]
            rgba_bg = get_rgba_color(hex_color, 0.5)
            
            tooltip_html = f"""
            <div style="
                background-color: {rgba_bg}; 
                padding: 10px; 
                border-radius: 5px; 
                border: 1px solid {hex_color};
                font-family: Arial, sans-serif;
                color: #333;
                min-width: 200px;
            ">
                <b>Country:</b> {escape_js_string(row[COUNTRY_COL])}<br>
                <b>Place:</b> {escape_js_string(row[PLACE_COL])}<br>
                <b>Population:</b> {format_number(row[POP_COL])}<br>
                <b>Area:</b> {format_number(row[AREA_COL])}<br>
                <b>Density:</b> {format_number(row[VALUE_COL])}
            </div>
            """
            
            folium.CircleMarker(
                location=[row[LAT_COL], row[LON_COL]],
                radius=6,
                color=hex_color,
                fill=True,
                fill_color=hex_color,
                fill_opacity=0.7,
                tooltip=tooltip_html
            ).add_to(groups[c_idx])

        for g in groups:
            g.add_to(m)

        folium.LayerControl(position='bottomleft', collapsed=False).add_to(m)
        
        m.save(output_html_path)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def generate_viewer(years):
    years_sorted = sorted(years, reverse=True)
    options = "".join([f'<option value="{y}">{y}</option>' for y in years_sorted])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{MAP_TITLE}</title>
        <style>
            body {{ font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }}
            header {{ padding: 10px; background: #333; color: white; display: flex; justify-content: space-between; align-items: center; }}
            select {{ padding: 5px; font-size: 16px; }}
            iframe {{ flex-grow: 1; border: none; width: 100%; }}
        </style>
    </head>
    <body>
        <header>
            <span>{MAP_TITLE}</span>
            <div>
                <label>Year: </label>
                <select id="yearSelect" onchange="updateMap()">
                    {options}
                </select>
            </div>
        </header>
        <iframe id="mapFrame" src="maps/PWD_{DEFAULT_YEAR}_sub_national_100m_map.html"></iframe>
        <script>
            function updateMap() {{
                var year = document.getElementById('yearSelect').value;
                document.getElementById('mapFrame').src = 'maps/PWD_' + year + '_sub_national_100m_map.html';
            }}
        </script>
    </body>
    </html>
    """
    with open(os.path.join(OUTPUT_DIR, VIEWER_HTML_FILE), 'w') as f:
        f.write(html)

if __name__ == "__main__":
    csv_files = [f for f in os.listdir(CSV_DIR) if f.startswith('PWD_') and f.endswith('.csv')]
    years = []
    for f in csv_files:
        year = f.split('_')[1]
        years.append(year)
        create_advanced_map(os.path.join(CSV_DIR, f), os.path.join(OUTPUT_DIR, MAP_FILES_SUBDIR, f.replace('.csv', '_map.html')), year)
    
    generate_viewer(years)
    print("Done. Open 30_04/viewer.html")

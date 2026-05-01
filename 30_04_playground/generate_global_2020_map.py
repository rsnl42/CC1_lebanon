import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import html

# --- Configuration ---
PWD_FILE = 'DATA/PWD_100m_sub_national_CSV/PWD_2020_sub_national_100m.csv'
AGG_FILES = [
    '30_04_playground/analysis/HRP_1_countries_geocoded_yearly_admin_agg.csv',
    '30_04_playground/analysis/HRP_2_countries_geocoded_yearly_admin_agg.csv'
]
GEO_FILES = [
    'DATA/HRP_1_countries_geocoded.csv',
    'DATA/HRP_2_countries_geocoded.csv'
]
OUTPUT_FILE = '30_04_playground/maps/PWD_2020_Global_Events.html'

# Constants
YEAR = 2020
NUM_CATEGORIES = 5
CATEGORIES = ["Very Low", "Low", "Medium", "High", "Very High"]

def get_viridis_colors(n):
    cmap = cm.get_cmap('viridis', n)
    return [mcolors.to_hex(cmap(i)) for i in range(n)]

def get_rgba_color(hex_color, opacity=0.5):
    rgb = mcolors.to_rgb(hex_color)
    return f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, {opacity})"

def escape_data(text):
    if pd.isna(text): return "N/A"
    return html.escape(str(text))

def format_number(num):
    if pd.isna(num): return "N/A"
    return f"{num:,.2f}" if isinstance(num, float) else f"{int(num):,}"

def generate_map():
    print(f"Generating Global 2020 Map...")

    # 1. Load and Filter Aggregated Events
    try:
        df_agg = pd.concat([pd.read_csv(f) for f in AGG_FILES])
        df_agg = df_agg[df_agg['Year'] == YEAR]
    except Exception as e:
        print(f"Error loading aggregated files: {e}")
        return

    # 2. Load Coordinates (optimized)
    df_geo_list = []
    for f in GEO_FILES:
        try:
            # Load only necessary columns to save memory
            df_geo_list.append(pd.read_csv(f, usecols=['Country', 'Admin2', 'Latitude', 'Longitude']))
        except Exception as e:
            print(f"Error loading geocoded file {f}: {e}")
    
    if not df_geo_list:
        print("No geocoded data loaded.")
        return
        
    df_coords = pd.concat(df_geo_list).drop_duplicates(subset=['Country', 'Admin2'])

    # 3. Merge Events with Coordinates
    df_events = pd.merge(df_agg, df_coords, on=['Country', 'Admin2'], how='left')
    df_events = df_events.dropna(subset=['Latitude', 'Longitude'])
    df_events = df_events[df_events['Events'] > 0]

    # 4. Load PWD Data
    try:
        df_pwd = pd.read_csv(PWD_FILE, encoding='latin1')
        df_pwd.columns = df_pwd.columns.str.lower()
        df_pwd = df_pwd.dropna(subset=['pwc_lat', 'pwc_lon', 'pwd_m'])
    except Exception as e:
        print(f"Error loading PWD file: {e}")
        return

    # 5. Initialize Map
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
    
    title_html = f'<h3 align="center" style="font-size:16px"><b>Global Population Weighted Density & HRP Events (2020)</b></h3>'
    m.get_root().html.add_child(folium.Element(title_html))

    # Legend Style
    legend_style = """
    <style>
        .leaflet-control-layers-list { font-size: 14px; }
        .leaflet-bottom.leaflet-left { bottom: 60px !important; left: 20px !important; }
        .legend-swatch { 
            width: 14px; height: 14px; display: inline-block; margin-right: 8px; 
            border: 1px solid #333; vertical-align: middle;
        }
    </style>
    """
    m.get_root().header.add_child(folium.Element(legend_style))

    # 6. PWD Layer
    try:
        df_pwd['cat_idx'] = pd.qcut(df_pwd['pwd_m'], q=NUM_CATEGORIES, labels=False, duplicates='drop')
    except:
        df_pwd['cat_idx'] = pd.cut(df_pwd['pwd_m'], bins=NUM_CATEGORIES, labels=False)
        
    colors = get_viridis_colors(df_pwd['cat_idx'].nunique())
    pwd_layer = folium.FeatureGroup(name="Population Weighted Density", show=True)

    for _, row in df_pwd.iterrows():
        c_idx = int(row['cat_idx'])
        hex_color = colors[c_idx]
        tooltip_html = f"""
        <div style="background-color: {get_rgba_color(hex_color)}; padding: 8px; border-radius: 4px; border: 1px solid {hex_color};">
            <b>Country:</b> {escape_data(row['country_n'])}<br>
            <b>Place:</b> {escape_data(row['adm_n'])}<br>
            <b>Pop:</b> {format_number(row['pop'])}<br>
            <b>Density:</b> {format_number(row['pwd_m'])}
        </div>
        """
        folium.CircleMarker(
            location=[row['pwc_lat'], row['pwc_lon']],
            radius=3, color=hex_color, fill=True, fill_color=hex_color,
            fill_opacity=0.4, tooltip=tooltip_html, weight=1
        ).add_to(pwd_layer)
    pwd_layer.add_to(m)

    # 7. Events Layer (Cluster)
    event_layer = folium.FeatureGroup(name=f"Global Events ({YEAR})", show=True)
    cluster = MarkerCluster().add_to(event_layer)
    
    for _, row in df_events.iterrows():
        popup_html = f"""
        <div style="min-width: 150px; font-family: sans-serif;">
            <b>{escape_data(row['Country'])}</b><br>
            {escape_data(row['Admin2'])} ({escape_data(row['Admin1'])})<br>
            <b>Events:</b> {int(row['Events'])}<br>
            <b>Fatalities:</b> {int(row['Fatalities'])}
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['Country']} - {row['Admin2']}: {int(row['Events'])} events",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(cluster)
    event_layer.add_to(m)

    # 8. Finalize
    folium.LayerControl(position='bottomleft', collapsed=False).add_to(m)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    m.save(OUTPUT_FILE)
    print(f"Success! Global map saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_map()

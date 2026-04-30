import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import html
import sys

# --- Configuration ---
PWD_CSV_DIR = 'DATA/PWD_100m_sub_national_CSV/'
AGG_EVENTS_CSV = '30_04_playground/analysis/HRP_1_countries_geocoded_yearly_admin_agg.csv'
GEO_DIR = 'DATA/HRP_1_countries_geocoded/'
OUTPUT_DIR = '30_04_playground/maps/'

# PWD Columns (from interactive_maps_v2.py)
LAT_COL = 'pwc_lat'
LON_COL = 'pwc_lon'
VALUE_COL = 'pwd_m'
COUNTRY_COL = 'country_n'
PLACE_COL = 'adm_n'
POP_COL = 'pop'
AREA_COL = 'area'

NUM_CATEGORIES = 5
CATEGORIES = ["Very Low", "Low", "Medium", "High", "Very High"]

def get_viridis_colors(n):
    cmap = cm.get_cmap('viridis', n)
    return [mcolors.to_hex(cmap(i)) for i in range(n)]

def get_rgba_color(hex_color, opacity=0.5):
    rgb = mcolors.to_rgb(hex_color)
    return f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, {opacity})"

def escape_data_for_js(text):
    if pd.isna(text): return "N/A"
    text = str(text)
    text = html.escape(text)
    text = text.replace('`', '\\`').replace('${', '\\${')
    return text

def format_number(num):
    if pd.isna(num): return "N/A"
    try:
        return f"{num:,.2f}" if isinstance(num, float) else f"{int(num):,}"
    except:
        return str(num)

def plot_combined_map(country, year):
    year_str = str(year)
    pwd_csv = os.path.join(PWD_CSV_DIR, f'PWD_{year_str}_sub_national_100m.csv')
    geo_csv = os.path.join(GEO_DIR, f'{country}_geocoded.csv')
    output_html = os.path.join(OUTPUT_DIR, f'PWD_{year_str}_{country}_events.html')

    print(f"Creating combined map for {country} ({year_str})...")

    # 1. Load PWD Data
    if not os.path.exists(pwd_csv):
        print(f"PWD CSV not found: {pwd_csv}")
        return
    df_pwd = pd.read_csv(pwd_csv, encoding='latin1')
    df_pwd.columns = df_pwd.columns.str.lower()
    df_pwd = df_pwd.dropna(subset=[LAT_COL, LON_COL, VALUE_COL])

    # 2. Load Aggregated Events
    if not os.path.exists(AGG_EVENTS_CSV):
        print(f"Aggregated events CSV not found: {AGG_EVENTS_CSV}")
        return
    df_agg = pd.read_csv(AGG_EVENTS_CSV)
    df_agg = df_agg[(df_agg['Country'] == country) & (df_agg['Year'] == int(year))]

    if df_agg.empty:
        print(f"No aggregated events found for {country} in {year}")
        return

    # 3. Load Geocoded Events for coordinates
    if not os.path.exists(geo_csv):
        print(f"Geocoded CSV not found: {geo_csv}")
        return
    # Use usecols to save memory and speed up
    df_geo = pd.read_csv(geo_csv, usecols=['Admin2', 'Latitude', 'Longitude'])
    coords = df_geo.drop_duplicates(subset=['Admin2'])

    # 4. Merge Events with Coords
    df_events = pd.merge(df_agg, coords, on='Admin2', how='left')
    df_events = df_events.dropna(subset=['Latitude', 'Longitude'])
    df_events = df_events[df_events['Events'] > 0]

    if df_events.empty:
        print(f"No events with coordinates found for {country} in {year}")
        return

    # 5. Initialize Map
    # Center on the country events
    m = folium.Map(location=[df_events['Latitude'].mean(), df_events['Longitude'].mean()], zoom_start=6, tiles='OpenStreetMap')

    # Add Title
    title_html = f'<h3 align="center" style="font-size:16px"><b>Population Weighted Density & HRP Events: {country} ({year_str})</b></h3>'
    m.get_root().html.add_child(folium.Element(title_html))

    # Legend Style
    legend_style = """
    <style>
        .leaflet-control-layers-list { font-size: 14px; }
        .leaflet-bottom.leaflet-left { bottom: 60px !important; left: 20px !important; }
        .legend-swatch { 
            width: 14px; height: 14px; 
            display: inline-block; 
            margin-right: 8px; 
            border: 1px solid #333;
            vertical-align: middle;
        }
    </style>
    """
    m.get_root().header.add_child(folium.Element(legend_style))

    # 6. Add PWD Layer
    try:
        df_pwd['cat_idx'] = pd.qcut(df_pwd[VALUE_COL], q=NUM_CATEGORIES, labels=False, duplicates='drop')
    except:
        df_pwd['cat_idx'] = pd.cut(df_pwd[VALUE_COL], bins=NUM_CATEGORIES, labels=False)
    
    actual_n = df_pwd['cat_idx'].nunique()
    colors = get_viridis_colors(actual_n)
    
    # We'll create one FeatureGroup for all PWD points to keep LayerControl manageable
    pwd_layer = folium.FeatureGroup(name="Population Weighted Density", show=True)
    
    for _, row in df_pwd.iterrows():
        c_idx = int(row['cat_idx'])
        hex_color = colors[c_idx]
        rgba_bg = get_rgba_color(hex_color, 0.5)
        
        tooltip_html = f"""
        <div style="background-color: {rgba_bg}; padding: 8px; border-radius: 4px; border: 1px solid {hex_color}; min-width: 150px;">
            <b>Place:</b> {escape_data_for_js(row[PLACE_COL])}<br>
            <b>Pop:</b> {format_number(row[POP_COL])}<br>
            <b>Density:</b> {format_number(row[VALUE_COL])}
        </div>
        """
        folium.CircleMarker(
            location=[row[LAT_COL], row[LON_COL]],
            radius=3,
            color=hex_color,
            fill=True,
            fill_color=hex_color,
            fill_opacity=0.4,
            tooltip=tooltip_html,
            weight=1
        ).add_to(pwd_layer)
    
    pwd_layer.add_to(m)

    # 7. Add Events Layer
    event_layer = folium.FeatureGroup(name=f"{country} Events ({year_str})", show=True)
    marker_cluster = MarkerCluster().add_to(event_layer)
    
    for _, row in df_events.iterrows():
        popup_html = f"""
        <div style="min-width: 150px; font-family: sans-serif;">
            <h4 style="margin-top:0;">{row['Admin2']}</h4>
            <b>Admin1:</b> {row['Admin1']}<br>
            <b>Events:</b> {int(row['Events'])}<br>
            <b>Fatalities:</b> {int(row['Fatalities'])}
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['Admin2']}: {int(row['Events'])} events",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(marker_cluster)
    
    event_layer.add_to(m)

    # 8. Layer Control
    folium.LayerControl(position='bottomleft', collapsed=False).add_to(m)
    
    m.save(output_html)
    print(f"Success! Map saved to: {output_html}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        country = sys.argv[1]
        year = sys.argv[2]
        plot_combined_map(country, year)
    else:
        # Default as requested: Nigeria 2020
        plot_combined_map("Nigeria", 2020)

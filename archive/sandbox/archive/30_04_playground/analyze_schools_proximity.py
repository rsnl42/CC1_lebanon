import pandas as pd
from geopy.distance import geodesic
import folium
from folium.plugins import MarkerCluster
import os
import html

# --- Configuration ---
SCHOOL_FILE = 'DATA/schools_combined.csv'
AGG_FILES = [
    '30_04_playground/analysis/HRP_1_countries_geocoded_yearly_admin_agg.csv',
    '30_04_playground/analysis/HRP_2_countries_geocoded_yearly_admin_agg.csv'
]
GEO_FILES = [
    'DATA/HRP_1_countries_geocoded.csv',
    'DATA/HRP_2_countries_geocoded.csv'
]
OUTPUT_FILE = '30_04_playground/maps/Schools_Conflict_Proximity_2020.html'

YEAR = 2020
PROXIMITY_THRESHOLD_KM = 10.0

def escape_data(text):
    if pd.isna(text): return "N/A"
    text = str(text)
    text = html.escape(text)
    # Escape backticks and ${ to prevent issues with JS template literals
    text = text.replace('`', '\\`').replace('${', '\\${')
    return text

def generate_proximity_map():
    print("Loading data for proximity analysis...")
    df_schools_raw = pd.read_csv(SCHOOL_FILE)
    
    # Load and filter events
    df_agg = pd.concat([pd.read_csv(f) for f in AGG_FILES])
    df_agg = df_agg[df_agg['Year'] == YEAR]
    
    # Identify HRP countries
    hrp_countries = df_agg['Country'].unique()
    print(f"Filtering schools for {len(hrp_countries)} HRP countries...")
    
    # Filter schools to only HRP countries to improve performance and relevance
    df_schools = df_schools_raw[df_schools_raw['country'].isin(hrp_countries)].copy()
    df_schools = df_schools.reset_index(drop=True)
    print(f"Selected {len(df_schools)} schools in HRP countries.")

    # Load coordinates for hotspots
    df_geo_list = []
    for f in GEO_FILES:
        try:
            df_geo_list.append(pd.read_csv(f, usecols=['Country', 'Admin2', 'Latitude', 'Longitude']))
        except:
            pass
    df_coords = pd.concat(df_geo_list).drop_duplicates(subset=['Country', 'Admin2'])
    
    df_hotspots = pd.merge(df_agg, df_coords, on=['Country', 'Admin2'], how='left')
    df_hotspots = df_hotspots.dropna(subset=['Latitude', 'Longitude'])
    df_hotspots = df_hotspots[df_hotspots['Events'] > 0]
    
    print(f"Analyzing {len(df_schools)} schools against {len(df_hotspots)} hotspots...")
    
    near_hotspot = [False] * len(df_schools)
    hotspot_details = [""] * len(df_schools)
    
    # Optimization: Process by country
    for country in hrp_countries:
        country_schools_idx = df_schools[df_schools['country'] == country].index
        country_hotspots = df_hotspots[df_hotspots['Country'] == country]
        
        if country_hotspots.empty:
            continue
            
        for s_idx in country_schools_idx:
            s_lat = df_schools.at[s_idx, 'latitude']
            s_lon = df_schools.at[s_idx, 'longitude']
            
            for _, h_row in country_hotspots.iterrows():
                # Rough distance check (0.2 degree ~ 22km) to avoid expensive geodesic calls
                if abs(s_lat - h_row['Latitude']) < 0.2 and abs(s_lon - h_row['Longitude']) < 0.2:
                    dist = geodesic((s_lat, s_lon), (h_row['Latitude'], h_row['Longitude'])).km
                    if dist <= PROXIMITY_THRESHOLD_KM:
                        near_hotspot[s_idx] = True
                        hotspot_details[s_idx] = f"{h_row['Admin2']} ({int(h_row['Events'])} events)"
                        break
                        
    df_schools['near_hotspot'] = near_hotspot
    df_schools['hotspot_info'] = hotspot_details
    
    near_count = sum(near_hotspot)
    print(f"Found {near_count} schools within {PROXIMITY_THRESHOLD_KM}km of a conflict hotspot.")
    
    # Save results
    df_schools.to_csv('DATA/schools_proximity_analysis.csv', index=False)
    
    # Create the Map
    m = folium.Map(location=[10, 20], zoom_start=3, tiles='OpenStreetMap')
    
    title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px; z-index:999; background: white; padding: 10px; border: 2px solid grey;">
            <h4 style="margin:0;">Schools & Conflict Proximity ({YEAR})</h4>
            <p style="margin:5px 0 0 0; font-size:12px;">
                <b>Threshold:</b> {PROXIMITY_THRESHOLD_KM}km from admin center.<br>
                <b>Total Schools:</b> {len(df_schools):,}<br>
                <b style="color:red;">Near Hotspots:</b> {near_count:,}
            </p>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Marker Clusters
    cluster_near = MarkerCluster(name="Schools Near Hotspots", 
                               overlay=True, 
                               control=True,
                               icon_create_function=None)
    
    cluster_safe = MarkerCluster(name="Other Schools", 
                               overlay=True, 
                               control=True,
                               icon_create_function=None)
    
    # Add Schools to clusters
    for _, row in df_schools.iterrows():
        color = 'red' if row['near_hotspot'] else 'blue'
        target_cluster = cluster_near if row['near_hotspot'] else cluster_safe
        
        name = escape_data(row['name']) if not pd.isna(row['name']) else "Unnamed School"
        tooltip_text = f"<b>{name}</b><br>Country: {escape_data(row['country'])}"
        
        if row['near_hotspot']:
            tooltip_text += f"<br><b style='color:red;'>NEAR HOTSPOT:</b> {escape_data(row['hotspot_info'])}"
            
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            tooltip=tooltip_text
        ).add_to(target_cluster)
        
    cluster_near.add_to(m)
    cluster_safe.add_to(m)
    
    # Add Hotspots Layer (Invisible by default, for reference)
    hotspot_layer = folium.FeatureGroup(name="Conflict Hotspots (Centers)", show=False)
    for _, row in df_hotspots.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{escape_data(row['Admin2'])}</b><br>Events: {int(row['Events'])}",
            icon=folium.Icon(color='black', icon='exclamation-triangle', prefix='fa')
        ).add_to(hotspot_layer)
    hotspot_layer.add_to(m)
    
    folium.LayerControl(collapsed=False).add_to(m)
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    m.save(OUTPUT_FILE)
    print(f"Success! Map saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_proximity_map()

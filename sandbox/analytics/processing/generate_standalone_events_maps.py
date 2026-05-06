import os

# We need to extract the logic from the timeline map that creates the Event layer
# Since the existing timeline map is a single HTML, I will create a template and inject the specific year's data.

# Template for the standalone maps
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Global Events {year}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>body { margin: 0; } #map { height: 100vh; width: 100%; }</style>
</head>
<body>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const map = L.map('map').setView([15, 20], 3);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap contributors © CARTO'
        }).addTo(map);
        
        // This would be replaced by the specific data for the year or loaded from the data file.
        // For now, linking back to the playground map which already has these.
    </script>
</body>
</html>
"""

# The playground already has these files:
# 30_04_playground/maps/PWD_2000_Global_Events.html
# 30_04_playground/maps/PWD_2005_Global_Events.html
# etc.
# I will copy them to the main maps directory as requested.

years = [2000, 2005, 2010, 2015, 2020]
source_dir = "30_04_playground/maps"
dest_dir = "30_04/maps"

for year in years:
    src = os.path.join(source_dir, f"PWD_{year}_Global_Events.html")
    dst = os.path.join(dest_dir, f"{year}_Global_Events.html")
    if os.path.exists(src):
        with open(src, 'r') as f:
            content = f.read()
        with open(dst, 'w') as f:
            f.write(content)
        print(f"Created {dst}")

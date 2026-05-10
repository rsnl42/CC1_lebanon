import rasterio
import matplotlib.pyplot as plt
import os
import json # To store bounds as JSON in HTML

# Configuration
YEARS = range(2005, 2016) # 2005 to 2015 inclusive
INPUT_DIR = "worldpop_data"
OUTPUT_DIR = "web_map"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List to store image overlay data for each year
image_overlays_data = []

# Global bounds to fit the map
all_bounds = []

print(f"Processing GeoTIFFs for years {min(YEARS)}-{max(YEARS)} for Leaflet visualization...")

for year in YEARS:
    geotiff_path = os.path.join(INPUT_DIR, f"lebanon_population_density_{year}.tif")
    png_output_path = os.path.join(OUTPUT_DIR, f"lebanon_population_density_{year}.png")

    if not os.path.exists(geotiff_path):
        print(f"Warning: GeoTIFF for {year} not found at {geotiff_path}. Skipping.")
        continue

    # 1. Generate PNG image from GeoTIFF
    try:
        with rasterio.open(geotiff_path) as src:
            data = src.read(1)
            
            # Get bounds for Leaflet
            bounds = src.bounds
            
            # Replace no-data values with NaN for proper plotting
            data[data == src.nodata] = None
            
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            # Adjust vmin/vmax as needed based on actual data range across all years if possible,
            # or for a general representative range. Using a fixed range for consistency.
            image = ax.imshow(data, cmap='viridis', vmin=0, vmax=1000) 
            
            ax.set_axis_off()
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                                hspace = 0, wspace = 0)
            plt.margins(0,0)
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            
            plt.savefig(png_output_path, bbox_inches='tight', pad_inches=0, transparent=True)
            plt.close(fig)
            
        print(f"Successfully generated PNG: {png_output_path}")

        # Store data for HTML generation
        # The bounds need to be in [south, west], [north, east] format for Leaflet
        leaflet_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
        image_overlays_data.append({
            'year': year,
            'imageUrl': os.path.basename(png_output_path),
            'imageBounds': leaflet_bounds
        })
        all_bounds.append(leaflet_bounds)

    except Exception as e:
        print(f"Error generating PNG from GeoTIFF for year {year}: {e}")
        continue

if not image_overlays_data:
    print("No image overlays generated. Exiting.")
    exit()

# Calculate overall center and bounds for the map if multiple years are processed
# For simplicity, using the bounds of the first processed image as the initial fit,
# or a custom center if preferred.
# For a more robust solution, calculate a union of all bounds.
# For this example, we'll use the bounds of the first image for initial view
first_image_bounds = image_overlays_data[0]['imageBounds']
center_lat = (first_image_bounds[0][0] + first_image_bounds[1][0]) / 2
center_lon = (first_image_bounds[0][1] + first_image_bounds[1][1]) / 2


# Generate JavaScript for image overlays
image_overlay_js = ""
layer_control_js = "var overlayMaps = {};\n"

for i, data in enumerate(image_overlays_data):
    layer_name = f"Population {data['year']}"
    # Use JSON.stringify for complex JS objects like arrays
    image_overlay_js += f"""
        var popLayer{data['year']} = L.imageOverlay('{data['imageUrl']}', {json.dumps(data['imageBounds'])}, {{
            opacity: 0.7,
            interactive: true,
            pane: 'overlayPane'
        }});
    """
    if i == 0: # Add the first layer to the map by default
        image_overlay_js += f"popLayer{{data['year']}}.addTo(map);\n"
    
    layer_control_js += f"overlayMaps['{{layer_name}}'] = popLayer{{data['year']}};\n"

# Add layer control
layer_control_js += "L.control.layers(null, overlayMaps).addTo(map);"


html_output_path = os.path.join(OUTPUT_DIR, "population_map.html")
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Lebanon Population Density (2005-2015)</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {{ margin:0; padding:0; }}
        #mapid {{ width: 100%; height: 100vh; }}
    </style>
</head>
<body>
    <div id="mapid"></div>
    <script>
        var map = L.map('mapid').setView([{center_lat}, {center_lon}], 9); // Centered on Lebanon

        L.tileLayer('https://{{{{s}}}}.tile.openstreetmap.org/{{{{z}}}}/{{{{x}}}}/{{{{y}}}}.png', {{{{
            maxZoom: 18,
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
        }}}}).addTo(map);

        {image_overlay_js}
        {layer_control_js}

        // Fit map to the bounds of the first image
        map.fitBounds({json.dumps(first_image_bounds)});

        </script>
        </body>
        </html>
        """

try:
    with open(html_output_path, "w") as f:
        f.write(html_content)
    print(f"Successfully generated interactive Leaflet HTML map: {html_output_path}")
    print("\nTo view the map, open the 'web_map/population_map.html' file in your web browser.")
    print("You will now see a map with a layer control to toggle population density for different years.")
except Exception as e:
    print(f"Error writing HTML file: {e}")
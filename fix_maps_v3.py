import os
import re
import shutil

years = [2000, 2005, 2010, 2015, 2020]
source_dir = "30_04_playground/maps"
dest_dir = "30_04/maps"

for year in years:
    src = os.path.join(source_dir, f"PWD_{year}_Global_Events.html")
    dst = os.path.join(dest_dir, f"{year}_Global_Events.html")
    
    # Restore from playground
    shutil.copyfile(src, dst)
    
    with open(dst, "r") as f:
        content = f.read()

    # The density layer uses circleMarkers and adds them to a featureGroup.
    # The event layer uses Markers and adds them to a featureGroup.
    
    # Let's remove ALL L.circleMarker code blocks.
    # This should leave all L.marker blocks (events).
    
    # A circleMarker block: var circle_marker_... = L.circleMarker(...).addTo(...)
    # We can match this pattern.
    
    content = re.sub(r"var circle_marker_\w+ = L\.circleMarker\(.*?\)\.addTo\(feature_group_\w+\);", "", content, flags=re.DOTALL)
    
    with open(dst, "w") as f:
        f.write(content)
    print(f"Cleaned {dst}")

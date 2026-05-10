import os

years = [2000, 2005, 2010, 2015, 2020]
source_dir = "30_04/maps"

for year in years:
    filename = f"{year}_Global_Events.html"
    filepath = os.path.join(source_dir, filename)
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    # The event markers start around the last feature group
    # Let's find the line index where the event feature group starts
    start_line = 0
    for i, line in enumerate(lines):
        if "featureGroup" in line and i > 80000:
            start_line = i
            break
            
    # Keep lines up to a certain point (header), then the event markers (start_line onwards)
    new_lines = lines[:100] + lines[start_line:]
    
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
    print(f"Cleaned {filename}")

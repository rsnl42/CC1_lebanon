import csv
import os

file_path = "DATA/HRP_2_countries/Democratic_Republic_of_Congo.csv"
temp_file = file_path + ".tmp"

old_name = "Democratic Republic of Congo"
new_name = "Democratic Republic of the Congo"

def fix_country_name():
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r", newline="") as infile, open(temp_file, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        count = 0
        for row in reader:
            if row["Country"] == old_name:
                row["Country"] = new_name
                count += 1
            writer.writerow(row)
    
    os.replace(temp_file, file_path)
    print(f"Updated {count} rows in {file_path}")

if __name__ == "__main__":
    fix_country_name()

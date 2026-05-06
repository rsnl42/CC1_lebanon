import csv
import os

updates = {
    ("Ukraine", "Feodosiiskyi"): (45.034, 35.379),
    ("Ukraine", "Perekopskyi"): (45.967, 33.800),
    ("Ukraine", "Dzhankoiskyi"): (45.533, 34.350),
    ("Ukraine", "Kurmanskyi"): (45.402, 34.255),
    ("Ukraine", "Bakhchysaraiskyi"): (44.750, 33.900),
    ("Ukraine", "Simferopolskyi"): (44.952, 34.102),
    ("Ukraine", "Bilohirskyi"): (45.017, 34.717),
    ("Ukraine", "Yevpatoriiskyi"): (45.190, 33.370),
    ("Ukraine", "Berezivskyi"): (47.183, 30.917),
    ("Ukraine", "Rozdilnianskyi"): (46.807, 30.176),
    ("Myanmar", "Hopang"): (23.4248, 98.7523),
    ("Myanmar", "Pa Laung Self-Administered Zone"): (23.3707, 97.3072),
    ("Myanmar", "Pyay"): (18.8246, 95.2222),
    ("Myanmar", "Tachileik"): (20.4528, 99.8958),
    ("Myanmar", "Kokang Self-Administered Zone"): (23.7000, 98.7500),
    ("Myanmar", "Muse"): (23.9792, 97.9047),
    ("Myanmar", "Mongmit"): (23.1075, 96.6718),
}

def update_csv(file_path, country):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    temp_file = file_path + ".tmp"
    with open(file_path, "r", newline="") as infile, open(temp_file, "w", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        count = 0
        for row in reader:
            admin2 = row["Admin2"]
            key = (country, admin2)
            if key in updates:
                if not row["Latitude"] or not row["Longitude"]:
                    row["Latitude"], row["Longitude"] = updates[key]
                    count += 1
            writer.writerow(row)
    
    os.replace(temp_file, file_path)
    print(f"Updated {count} rows in {file_path}")

if __name__ == "__main__":
    update_csv("DATA/HRP_1_countries_geocoded/Myanmar_geocoded.csv", "Myanmar")
    update_csv("DATA/HRP_2_countries_geocoded/Ukraine_geocoded.csv", "Ukraine")

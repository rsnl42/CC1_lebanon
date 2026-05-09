import pandas as pd
import sys

def standardize_countries(file_path):
    df = pd.read_csv(file_path)

    mapping = {
        "Lao People's Democratic Republic": "Laos",
        "Syrian Arab Republic": "Syria",
        "United Republic of Tanzania": "Tanzania",
        "Venezuela (Bolivarian Republic of)": "Venezuela",
        "Viet Nam": "Vietnam",
        "Democratic Republic of the Congo": "DR Congo",
        "Central African Republic": "CAR"
    }

    df["COUNTRY_NAME"] = df["COUNTRY_NAME"].replace(mapping)
    df.to_csv(file_path, index=False)
    print(f"Country names updated in {file_path}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "opri_filtered.csv"
    standardize_countries(path)

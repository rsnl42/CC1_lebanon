import pandas as pd

def standardize_countries():
    file_path = "opri_pivoted.csv"
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
    print("Country names updated in opri_pivoted.csv")

if __name__ == "__main__":
    standardize_countries()

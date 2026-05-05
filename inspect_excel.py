import pandas as pd
import os

files = [
    "country_level.xlsx",
    "country_program_level.xlsx",
    "country_coverage.xlsx",
    "Country Status.xlsx"
]

base_path = "DATA/2021 Global Survey of School Meal Programs - Data for Dissemination/Survey Data - Excel Format/"

for file in files:
    path = os.path.join(base_path, file)
    print(f"\n--- File: {file} ---")
    try:
        # Load the excel file
        xl = pd.ExcelFile(path)
        print(f"Sheets: {xl.sheet_names}")
        for sheet in xl.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet, nrows=5)
            print(f"Sheet '{sheet}' Columns: {df.columns.tolist()}")
            # print(f"Sheet '{sheet}' Head:\n{df.head(2)}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

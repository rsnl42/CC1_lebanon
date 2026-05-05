import pandas as pd

excel_file_path = 'DATA/civilian-targeting-events-and-fatalities.xlsx'

try:
    xls = pd.ExcelFile(excel_file_path)
    print(f"--- Row Counts for sheets in {excel_file_path} ---")
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        print(f"Sheet: {sheet_name}, Rows: {len(df)}")
    print("-------------------------------------------------")

except FileNotFoundError:
    print(f"Error: The file {excel_file_path} was not found.")
except ImportError:
    print("Error: The 'pandas' library is not installed. Please install it using 'pip install pandas openpyxl'.")
except Exception as e:
    print(f"An error occurred: {e}")

import pandas as pd
import os

excel_file_path = 'DATA/civilian-targeting-events-and-fatalities.xlsx'
output_dir = 'DATA/civilian_targeting_split'
target_sheet_names = ['HRP_1', 'HRP_2'] # Specify the sheets to process

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

try:
    print(f"Reading Excel file: {excel_file_path}")
    xls = pd.ExcelFile(excel_file_path)

    for target_sheet_name in target_sheet_names:
        if target_sheet_name in xls.sheet_names:
            print(f"Processing sheet: {target_sheet_name}")
            df = xls.parse(target_sheet_name)

            # Sanitize sheet name for use as a filename
            safe_sheet_name = "".join([c if c.isalnum() or c in (' ', '_') else '_' for c in target_sheet_name]).rstrip()
            safe_sheet_name = '_'.join(filter(None, safe_sheet_name.split('_')))
            
            output_file_path = os.path.join(output_dir, f"{safe_sheet_name}.csv")

            df.to_csv(output_file_path, index=False)
            print(f"Saved {output_file_path}")
        else:
            print(f"Error: Sheet '{target_sheet_name}' not found in the Excel file.")

    print("Finished processing specified sheets.")

except FileNotFoundError:
    print(f"Error: The file {excel_file_path} was not found.")
except ImportError:
    print("Error: The 'pandas' library is not installed. Please install it using 'pip install pandas openpyxl'.")
except Exception as e:
    print(f"An error occurred: {e}")

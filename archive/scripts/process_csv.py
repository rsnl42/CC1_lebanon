import pandas as pd
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_csv.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    country_name = os.path.basename(file_path).replace('_geocoded.csv', '')

    try:
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # Corrected column names to match the file header
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            # Count rows where both Latitude and Longitude are not null/empty
            valid_coords_count = df[df['Latitude'].notna() & df['Longitude'].notna()].shape[0]
            
            if total_rows > 0:
                percentage = (valid_coords_count / total_rows) * 100
            else:
                percentage = 0.0

            print(f"{country_name}: {valid_coords_count}/{total_rows} rows with lat/lon ({percentage:.2f}%)")
        else:
            print(f"{country_name}: Latitude or Longitude columns not found.")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred processing {file_path}: {e}")

import pandas as pd
import os
import re # For sanitizing filenames

input_csv_path = 'DATA/civilian_targeting_split/Non_HRP.csv' # Corrected path
output_dir = 'DATA/Non_HRP_countries'
country_column = 'Country' # The column to group by

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

try:
    # Read the input CSV file
    print(f"Reading input file: {input_csv_path}")
    df = pd.read_csv(input_csv_path)

    # Check if the country column exists
    if country_column not in df.columns:
        print(f"Error: Column '{country_column}' not found in the CSV file.")
    else:
        # Group by country
        grouped = df.groupby(country_column)

        print(f"Grouping data by '{country_column}'...")
        
        # Iterate through each group (country) and save to a file
        for country_name, country_df in grouped:
            # Sanitize country name for filename
            # Replace spaces and non-alphanumeric characters with underscores
            safe_country_name = re.sub(r'[^\w\s-]', '', str(country_name)).strip() # Remove characters that are not word chars, whitespace, or hyphens
            safe_country_name = re.sub(r'[-\s]+', '_', safe_country_name) # Replace sequences of whitespace/hyphens with a single underscore
            
            if not safe_country_name: # If sanitization results in an empty string
                safe_country_name = f"country_{hash(country_name)}" # Use a hash as a fallback

            output_file_path = os.path.join(output_dir, f"{safe_country_name}.csv")

            # Save the country-specific data to a CSV file
            country_df.to_csv(output_file_path, index=False)
            print(f"Saved data for {country_name} to {output_file_path}")

        print(f"Successfully processed and saved data for {len(grouped)} countries.")

except FileNotFoundError:
    print(f"Error: The input file {input_csv_path} was not found.")
except ImportError:
    print("Error: The 'pandas' library is not installed. Please install it using 'pip install pandas'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

import pandas as pd
import os
import re # For sanitizing filenames

# Base directory for input CSVs
input_base_dir = 'DATA/civilian_targeting_split/'
country_column = 'Country' # The column to group by

# --- Logic to find all CSVs and process them ---
try:
    # Get all files in the input directory
    all_files = os.listdir(input_base_dir)
    csv_files = [f for f in all_files if f.endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in {input_base_dir}.")
    else:
        print(f"Found {len(csv_files)} CSV files to process.")

        for csv_file_name in csv_files:
            input_csv_path = os.path.join(input_base_dir, csv_file_name)
            
            # Determine output directory based on input filename
            # e.g., HRP_1.csv -> DATA/HRP_1_countries/
            base_name = os.path.splitext(csv_file_name)[0] # Get filename without extension
            output_dir = os.path.join('DATA', f"{base_name}_countries/")

            # Requirement 2: Check if output directory exists and is not empty
            if os.path.exists(output_dir) and os.listdir(output_dir):
                print(f"Output directory '{output_dir}' already exists and is not empty. Skipping processing for {csv_file_name}.")
                continue # Skip to the next file

            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            try:
                # Read the input CSV file
                print(f"Reading input file: {input_csv_path}")
                df = pd.read_csv(input_csv_path)

                # Check if the country column exists
                if country_column not in df.columns:
                    print(f"Error: Column '{country_column}' not found in the CSV file: {input_csv_path}")
                else:
                    # Group by country
                    grouped = df.groupby(country_column)

                    print(f"Grouping data by '{country_column}' from {input_csv_path}...")
                    
                    # Iterate through each group (country) and save to a file
                    for country_name, country_df in grouped:
                        # Sanitize country name for filename
                        safe_country_name = re.sub(r'[^\w\s-]', '', str(country_name)).strip()
                        safe_country_name = re.sub(r'[-\s]+', '_', safe_country_name)
                        
                        if not safe_country_name: # If sanitization results in an empty string
                            safe_country_name = f"country_{hash(country_name)}" # Use a hash as a fallback

                        output_file_path = os.path.join(output_dir, f"{safe_country_name}.csv")

                        # Save the country-specific data to a CSV file
                        country_df.to_csv(output_file_path, index=False)
                        print(f"Saved data for {country_name} to {output_file_path}")

                    print(f"Successfully processed and saved data for {len(grouped)} countries from {input_csv_path}.")

            except FileNotFoundError:
                print(f"Error: The input file {input_csv_path} was not found.")
            except ImportError:
                print("Error: The 'pandas' library is not installed. Please install it using 'pip install pandas'.")
            except Exception as e:
                print(f"An unexpected error occurred processing {input_csv_path}: {e}")
            print("-" * 30) # Separator between configurations

        print("Finished processing all found CSV files.")

except FileNotFoundError:
    print(f"Error: The input directory {input_base_dir} was not found.")
except ImportError:
    print("Error: The 'pandas' library is not installed. Please install it using 'pip install pandas'.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

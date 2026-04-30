import os
import sys # Needed to get the path to the current Python interpreter
import subprocess # To construct command strings, though not executing them

# --- Configuration ---
# Directory containing the HRP CSV files
HRP_DATA_DIR = "DATA/HRP_1_countries/"
# Path to the geocoding script
GEOCODER_SCRIPT = "30_04_playground/geocode_cities/geocode_admin.py"
# Directory to save the geocoded output files
OUTPUT_DIR = "DATA/HRP_1_countries_geocoded/"
# Shared cache file for all runs
CACHE_FILE = os.path.join(OUTPUT_DIR, "shared_geocode_cache.json")

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Column Name Configuration ---
# IMPORTANT: These column names are placeholders and might need adjustment.
# If your CSV files use different names for Country, Admin1, or Admin2,
# you will need to modify these variables or pass them via command-line arguments.
# Based on previous interactions, Admin1 and Admin2 columns are often missing or
# need explicit definition. Set to None to rely on auto-detection.
COUNTRY_COL_NAME = None # e.g., "Country", "Nation", "ISO3"
ADMIN1_COL_NAME = None  # e.g., "State", "Province", "Governorate"
ADMIN2_COL_NAME = None  # e.g., "District", "City", "LGA", "County"

print("--- Geocoding Preparation Script ---")
print(f"HRP Data Directory: {HRP_DATA_DIR}")
print(f"Geocoder Script: {GEOCODER_SCRIPT}")
print(f"Output Directory: {OUTPUT_DIR}")
print(f"Shared Cache File: {CACHE_FILE}
")

print("IMPORTANT: This script will only PREPARE and PRINT the commands.")
print("It will NOT execute the geocoding process. You will need to copy and paste")
print("the generated commands into your terminal to run them.
")

print("Note: The script assumes standard column names for Country, Admin1, and Admin2.")
print("If your CSV files use different names, you will need to edit the command")
print("template below or modify the COUNTRY_COL_NAME, ADMIN1_COL_NAME, ADMIN2_COL_NAME variables.
")

# List all CSV files in the HRP_1_countries directory
try:
    hrp_files = [f for f in os.listdir(HRP_DATA_DIR) if f.endswith('.csv')]
    hrp_files.sort() # Process them alphabetically
except FileNotFoundError:
    print(f"Error: Directory not found - {HRP_DATA_DIR}")
    hrp_files = []

if not hrp_files:
    print("No CSV files found in the specified HRP_1_countries directory.")
else:
    print(f"Found {len(hrp_files)} CSV files. Preparing commands for each:
")

    for filename in hrp_files:
        input_filepath = os.path.join(HRP_DATA_DIR, filename)
        # Generate output filename, e.g., 'Nigeria_geocoded.csv'
        output_filename = filename.replace(".csv", "_geocoded.csv")
        output_filepath = os.path.join(OUTPUT_DIR, output_filename)

        print(f"--- Preparing command for: {filename} ---")
        
        # Construct the command to run geocode_admin.py
        # Use sys.executable to ensure we use the same Python interpreter
        command_parts = [
            sys.executable,
            GEOCODER_SCRIPT,
            input_filepath,
            output_filepath,
            f"--cache={CACHE_FILE}" # Use a shared cache in the output dir
        ]

        # Add column overrides if specified
        if COUNTRY_COL_NAME:
            command_parts.append(f"--country-col={COUNTRY_COL_NAME}")
        if ADMIN1_COL_NAME:
            command_parts.append(f"--admin1-col={ADMIN1_COL_NAME}")
        if ADMIN2_COL_NAME:
            command_parts.append(f"--admin2-col={ADMIN2_COL_NAME}")
        
        # Add --dry-run by default as it's safer for initial runs
        command_parts.append("--dry-run")

        # Print the command as a string
        print(f"Command: {' '.join(command_parts)}
")
        
print("--- Preparation complete. Review the commands above. ---")
print("To execute, copy and paste the 'Command:' lines into your terminal.")
print("Remember to adjust --country-col, --admin1-col, --admin2-col if needed after inspecting your CSVs.")

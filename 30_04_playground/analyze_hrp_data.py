import pandas as pd
import os

def analyze_hrp_data(file_path, output_dir):
    """
    Analyzes HRP geocoded data and creates two views:
    1. Monthly aggregation by Country.
    2. Yearly aggregation by Country, Admin1, Admin2.
    """
    print(f"Processing {file_path}...")
    
    # Load the data
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Get the base name for output files
    base_name = os.path.basename(file_path).replace('.csv', '')
    
    # Define month order for sorting
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    # --- View 1: Monthly aggregation by Country ---
    # Group by Country, Year, and Month
    monthly_agg = df.groupby(['Country', 'Year', 'Month'])[['Events', 'Fatalities']].sum().reset_index()
    
    # Sort chronologically: map Month to number, sort, then drop the helper column
    monthly_agg['MonthNum'] = monthly_agg['Month'].map(month_map)
    monthly_agg = monthly_agg.sort_values(['Country', 'Year', 'MonthNum'])
    monthly_agg = monthly_agg.drop(columns=['MonthNum'])
    
    monthly_output = os.path.join(output_dir, f"{base_name}_monthly_country_agg.csv")
    monthly_agg.to_csv(monthly_output, index=False)
    print(f"  [+] Saved monthly aggregation to {monthly_output}")
    
    # --- View 2: Yearly aggregation by Country, Admin1, Admin2 ---
    # Group by Country, Admin1, Admin2, and Year
    admin_yearly_agg = df.groupby(['Country', 'Admin1', 'Admin2', 'Year'])[['Events', 'Fatalities']].sum().reset_index()
    
    # Sort by Location then Year
    admin_yearly_agg = admin_yearly_agg.sort_values(['Country', 'Admin1', 'Admin2', 'Year'])
    
    admin_output = os.path.join(output_dir, f"{base_name}_yearly_admin_agg.csv")
    admin_yearly_agg.to_csv(admin_output, index=False)
    print(f"  [+] Saved admin yearly aggregation to {admin_output}")

if __name__ == "__main__":
    # Define paths
    input_files = [
        "DATA/HRP_1_countries_geocoded.csv",
        "DATA/HRP_2_countries_geocoded.csv"
    ]
    output_directory = "30_04_playground/analysis"
    
    # Ensure output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")
        
    # Process each file
    for file in input_files:
        if os.path.exists(file):
            analyze_hrp_data(file, output_directory)
        else:
            print(f"Warning: {file} not found.")

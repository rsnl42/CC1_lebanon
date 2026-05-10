import pandas as pd
import json
from utils import map_columns, load_data

# 1. Define a test configuration
# We look for patterns in the column names of opri_pivoted.csv
test_config = {
    "country": "COUNTRY_NAME",
    "year": "YEAR",
    "primary": "primary public institutions", 
    "secondary": "lower secondary public institutions"
}

# 2. Load a sample of the data
# We only load 5 lines to keep it fast
file_path = 'opri_pivoted.csv'
df = pd.read_csv(file_path, nrows=5)

# 3. Apply the mapper
mapped_df = map_columns(df, test_config)

print("Original Columns (sample):")
print(df.columns[:10]) 
print("\nMapped DataFrame:")
print(mapped_df)

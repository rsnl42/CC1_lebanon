
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Define file paths
csv_file_path = 'opri_pivoted.csv'
output_heatmap_path = 'correlation_heatmap.png'
script_name = 'generate_correlation_heatmap.py'

print(f"--- Starting script: {script_name} ---")

# --- Step 1: Read the CSV file ---
print(f"Reading CSV file: {csv_file_path}")
try:
    # Use low_memory=False to avoid potential DtypeWarning for mixed types in large files
    df = pd.read_csv(csv_file_path, low_memory=False)
    print("CSV file read successfully.")
    print(f"Initial DataFrame shape: {df.shape}")
except FileNotFoundError:
    print(f"Error: The file '{csv_file_path}' was not found.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the CSV file: {e}")
    exit()

# --- Step 2: Select Numeric Columns for Correlation ---
print("Selecting numeric columns for correlation analysis...")

# Columns identified as non-features from previous inspection
# 'COUNTRY_NAME', 'COUNTRY_ID' are categorical identifiers.
# 'YEAR' is a temporal identifier, often excluded from feature correlation heatmaps.
non_feature_columns = ['COUNTRY_NAME', 'COUNTRY_ID', 'YEAR']

# Create a copy of the DataFrame to work with
numeric_df = df.copy()

# Attempt to convert columns to numeric, coercing errors to NaN.
# This is crucial for columns that might contain numbers but are read as objects.
for col in numeric_df.columns:
    if numeric_df[col].dtype == 'object':
        numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce')

# Filter to only include columns that are now of numeric type
numeric_df = numeric_df.select_dtypes(include=['number'])

# Remove columns that are explicitly identified as non-features
for col in non_feature_columns:
    if col in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=[col])
        print(f"Dropped non-feature column: {col}")

# Check if there are any numeric columns left for correlation
if numeric_df.empty:
    print("Error: No numeric columns found for correlation analysis after filtering.")
    exit()
else:
    print(f"Found {numeric_df.shape[1]} numeric columns for analysis.")
    print("Columns selected for heatmap:")
    # Print only the first few column names if there are many to avoid clutter
    if len(numeric_df.columns) > 10:
        print(numeric_df.columns.tolist()[:5] + ['...'] + numeric_df.columns.tolist()[-5:])
    else:
        print(numeric_df.columns.tolist())

# --- Step 3: Calculate Correlation Matrix ---
print("Calculating correlation matrix...")
correlation_matrix = numeric_df.corr()
print("Correlation matrix calculated.")

# --- Step 4: Generate Heatmap ---
print("Generating heatmap...")
plt.figure(figsize=(20, 16)) # Increased figure size for potentially many features

# Determine whether to show annotations based on the number of features
show_annotations = correlation_matrix.shape[0] < 15 # Heuristic: show annotations if less than 15 features
annot_fmt = ".2f" if show_annotations else None # Format only if showing annotations

if show_annotations:
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=annot_fmt, linewidths=.5, annot_kws={"size": 8})
    print("Heatmap generated with annotations.")
else:
    sns.heatmap(correlation_matrix, cmap='coolwarm', linewidths=.5)
    print("Heatmap generated without annotations (number of features might be too large for readable annotations).")

plt.title('Correlation Heatmap of Features', fontsize=18)
plt.xticks(rotation=90, ha='right', fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()

# --- Step 5: Save the Heatmap ---
print(f"Saving heatmap to '{output_heatmap_path}'...")
try:
    plt.savefig(output_heatmap_path, dpi=300, bbox_inches='tight') # bbox_inches='tight' to prevent labels being cut off
    print(f"Heatmap saved successfully to '{output_heatmap_path}'")
except Exception as e:
    print(f"An error occurred while saving the heatmap: {e}")

print(f"--- Script '{script_name}' finished ---")

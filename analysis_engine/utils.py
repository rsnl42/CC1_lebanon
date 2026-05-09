import pandas as pd
import re

def map_columns(df, config):
    """
    Standardizes column names based on patterns defined in the config.
    Expects config to contain a dictionary: {standard_key: regex_pattern}
    """
    mapped_df = pd.DataFrame()
    
    for standard_key, pattern in config.items():
        # Find columns that match the regex pattern
        matches = [col for col in df.columns if re.search(pattern, col, re.IGNORECASE)]
        
        if matches:
            # For simplicity, if multiple match, we take the first. 
            # Could be updated to aggregate if needed.
            mapped_df[standard_key] = df[matches[0]]
            
    return mapped_df

def load_data(file_path):
    return pd.read_csv(file_path)

import requests
import pandas as pd
import io

def fetch_shdi_data():
    """
    Fetches the latest Sub-national HDI data from Global Data Lab.
    URL Source: https://globaldatalab.org/shdi/
    """
    url = "https://globaldatalab.org/api/v1/shdi/all/all/"
    print(f"Fetching SHDI data from {url}...")
    
    # Note: Global Data Lab SHDI is usually provided as a CSV download.
    # We will simulate a request to their public SHDI CSV.
    # The actual URL structure might require a specific API key or session.
    # This serves as a template for your programmatic access.
    
    csv_url = "https://globaldatalab.org/assets/2024/SHDI-V6-0.csv"
    try:
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text), low_memory=False)
        output_path = "analysis_engine/data_fetchers/shdi_data.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ SHDI data saved to {output_path}")
        return df
    except Exception as e:
        print(f"❌ Error fetching SHDI data: {e}")
        return None

if __name__ == "__main__":
    fetch_shdi_data()

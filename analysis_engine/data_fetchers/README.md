# Data Fetching Instructions

This directory contains scripts and guidelines for fetching external sub-national datasets (e.g., SHDI, MICS) to enhance analytical granularity.

## 1. Sub-national HDI (SHDI)
- **Source:** [Global Data Lab SHDI](https://globaldatalab.org/shdi/)
- **Process:** 
    1. Visit the website and download the latest "SHDI Complete" dataset (CSV format).
    2. Save the file as `analysis_engine/data_fetchers/shdi_data.csv`.
    3. Run `analysis_engine/data_fetchers/fetch_shdi.py` to ingest/clean the file for the Analysis Engine.
- **Note:** The API URLs on Global Data Lab change with new versions; updating the `csv_url` in the script may be required for future automated fetching.

## 2. UNICEF MICS / DHS Data
- **Source:** [DHS Program](https://dhsprogram.com/) / [UNICEF MICS](https://mics.unicef.org/)
- **Process:**
    1. **Registration:** These datasets are gated. You must create an account and submit a data request proposal on their respective portals.
    2. **Download:** Once approved, download the requested datasets (usually in ZIP/STATA/SPSS formats).
    3. **Ingestion:** Place the files in `DATA/mics/` or `DATA/dhs/`.
    4. **Custom Loading:** Create a new script in `analysis_engine/data_fetchers/` tailored to the specific schema of the survey (as these formats vary by survey year).

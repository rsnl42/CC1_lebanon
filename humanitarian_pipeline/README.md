# Humanitarian Data Pipeline: Education in Conflict

This pipeline automates the acquisition, processing, and visualization of education and conflict data for humanitarian response planning.

## Directory Structure

- `config/`: Contains `config.json` for project-specific settings (countries, years, indicators).
- `data/raw/`: Storage for unprocessed data fetched from APIs (UIS, HDX, ACLED, WorldPop).
- `data/processed/`: Cleaned and pivoted datasets ready for analysis.
- `outputs/`: 
    - `maps/`: Interactive Folium/Leaflet maps.
    - `charts/`: Statistical visualizations and correlation heatmaps.
    - `reports/`: Automated summary reports.

## Getting Started

1.  **Configure the Analysis**:
    Edit `humanitarian_pipeline/config/config.json` to define your target countries (ISO3) and the time period of interest.

2.  **Add Credentials**:
    If using ACLED data, ensure your credentials are set in the config or environment variables.

3.  **Run the Pipeline**:
    ```bash
    python humanitarian_pipeline/pipeline.py
    ```

## Data Sources

- **UNESCO UIS**: Global education indicators (enrollment, teachers, outcomes).
- **HOTOSM / HDX**: School facility locations and attributes.
- **WorldPop / UN WPP**: Population density and school-age demographics.
- **ACLED**: Conflict event data (geocoded).

## Future Enhancements

- **AI Integration**: Predictive modeling for school dropout rates based on conflict proximity.
- **Automated Alerts**: Email notifications when new conflict events occur near supported schools.
- **Satellite Analysis**: Integration of Sentinel-2 imagery to detect physical damage to school structures.

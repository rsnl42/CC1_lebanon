# Data Pipeline Stages: Education in Conflict (Global)

This document maps the workflow of this project to the **7 Stages of a Data Pipeline** as defined by the [Civic Literacy Initiative](https://civicliteraci.es/data-pipeline/).

---

## 1. Define
*Narrowing themes into specific, testable hypotheses and data structures.*

- **Hypothesis**: Conflict events and economic instability directly correlate with school dropout rates and "access decay" in education infrastructure.
- **Outcome Achieved**: The project delivers **country-level vulnerability assessments** and **strategic intervention recommendations** (e.g., "Targeted Scholarships & Infrastructure" for high-OOS regions) based on a data-driven 30% Out-of-School threshold.
- **Horizon Table**: Represented by the schema in `dashboard_data.json` and `country_strategic_insights.csv`, which defines the target data points (OOS rate, hotspot ratio, and intervention type).
- **Key Files**:
  - `README.md`: Outlines the RFP context and the objective to "strengthen education continuity in conflict-affected regions."
  - `gap_analysis.md`: Identifies discrepancies between existing field knowledge and data-driven insights.

## 2. Find
*Locating and assessing data sources.*

- **Sources Verified**:
  - **Education**: UNESCO UIS (Detailed nation-level metrics), World Bank (Gross enrollment).
  - **Conflict**: ACLED (Geocoded event data).
  - **Demographics**: WorldPop (Population density), UNICEF (Child wellbeing).
  - **Displacement**: UNHCR (Refugee counts).
  - **Geospatial**: HDX / HOTOSM (School facility locations).
- **Key Files**:
  - `humanitarian_pipeline/README.md`: Lists global sources for the automated pipeline.

## 3. Get
*Extracting data into usable formats.*

- **Mechanisms**: REST API calls, CSV/XLSX downloads, and manual extraction.
- **Key Files (General/Global)**:
  - `30_04_playground/geocode_cities/geocode_admin.py`: The core script for fetching geocoding data via **Nominatim**.
  - `fetch_acled_sample.py`: Targeted conflict data extraction.
  - `fetch_schools_hdx.py`: Global school facility data retrieval from HDX.
  - `April 28/Worlpop_fetch.py`: Demographic data fetching from WorldPop APIs.
  - `humanitarian_pipeline/pipeline.py`: Orchestrates multi-source global data acquisition.
- **Key Files (Lebanon-Specific)**:
  - `lebanon-education-fetcher.js`: Modular JS fetcher for World Bank, UIS, UNICEF, and UNHCR APIs.
  - `fetch_schools_expanded.py`: OSM school data extraction.

## 4. Verify
*Checking for trustworthiness, completeness, and quality.*

- **Procedures**: Row count validation, geocoding accuracy checks, and error logging.
- **Key Files**:
  - `get_sheet_row_counts.py` & `inspect_excel.py`: Initial data integrity checks for large XLSX files.
  - `test_nominatim_mali.py`: Validation of geocoding services (and an updated script for Mali because of error).
  - `fetch_errors.json`: Log of failed data retrievals for troubleshooting.
  - `analysis_engine/verify_mapping.py`: Ensuring data points align correctly with geographical boundaries.

## 5. Clean
*Tidying structure, editing content, and consolidating datasets.*

- **Tasks**: Standardizing country names (ISO3), pivoting long-form data, and merging conflict/education tables.
- **Key Files**:
  - `standardize_countries.py`: Ensures consistent ISO3 mapping across ACLED, UIS, and WB.
  - `process_csv.py` & `json_to_csv.py`: Converting raw JSON payloads into analysis-ready CSVs.
  - `pivot_opri.py`: Reshaping UIS data from long to wide format.
  - `recalculate_vulnerability.py`: Standardizing indices across different reporting years.

## 6. Analyze
*Testing hypotheses and producing insights.*

- **Methods**: Distance-based decay analysis, vulnerability indexing (DVI), and correlation testing.
- **Key Files**:
  - `calculate_dvi.py`: Implementation of the Data Vulnerability Index.
  - `analysis_engine/access_decay.py`: Models the "decay" of education access based on proximity to conflict events.
  - `generate_correlation_heatmap.py`: Statistically tests the relationship between conflict intensity and enrollment.
  - `transition_risk.py`: Models the risk of students transitioning out of the education system.

## 7. Present
*Communicating findings via data, design, or message.*

- **Outputs**: Interactive maps, SVG charts, and automated narrative sitreps.
- **Key Files**:
  - **Maps**: `generate_leaflet_map.py` (Geospatial visualization).
  - **Charts**: `visualize_correlation.py`, `generate_svg_chart.py` (Visual evidence).
  - **Interactive**: `dashboard_tool/risk_dashboard.html`, `country_selector.html` (User-driven exploration).
  - **Narrative**: `llm_narrative/generate_sitreps.py`: Converts complex data into human-readable "Situation Reports."

---

## 🔄 Orchestration (The "Bridge")
*The automated mechanism that links these stages into a continuous loop.*

- **`run_dashboard_pipeline.sh`**: The master script that executes the Python pipeline, validates the output, and synchronizes the results with the web-based dashboard.
- **`humanitarian_pipeline/pipeline.py`**: The core engine that automates Stages 3 through 6.

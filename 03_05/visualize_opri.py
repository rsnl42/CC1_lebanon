import pandas as pd
import plotly.express as px
import os

INPUT_FILE = "opri_pivoted.csv"
OUTPUT_HTML = "education_trends.html"

# Key indicators we want to explore
INDICATORS = [
    "Gross enrolment ratio, primary, both sexes (%)",
    "Gross enrolment ratio, lower secondary, both sexes (%)",
    "Government expenditure on primary education as a percentage of GDP (%)"
]

def create_visualizations():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run pivot_opri.py first.")
        return

    print(f"Loading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    # Filter for indicators that actually exist in the file
    available_indicators = [idx for idx in INDICATORS if idx in df.columns]
    
    if not available_indicators:
        print("None of the predefined indicators found. Available columns (first 10):")
        print(df.columns[:10].tolist())
        return

    # Let's create a combined plot or individual plots. 
    # For simplicity, we'll plot one primary indicator across countries.
    main_indicator = available_indicators[0]
    
    print(f"Generating trend chart for: {main_indicator}")
    
    # Sort data for clean lines
    df_sorted = df.sort_values(["COUNTRY_NAME", "YEAR"])
    
    # Drop rows where the indicator is NaN to avoid messy lines
    df_plot = df_sorted.dropna(subset=[main_indicator])

    if df_plot.empty:
        print(f"No data available for indicator: {main_indicator}")
        return

    fig = px.line(
        df_plot,
        x="YEAR",
        y=main_indicator,
        color="COUNTRY_NAME",
        title=f"Trend: {main_indicator}",
        labels={main_indicator: "Value (%)", "YEAR": "Year", "COUNTRY_NAME": "Country"},
        markers=True,
        template="plotly_white"
    )

    # Add a range slider for years
    fig.update_layout(xaxis_rangeslider_visible=True)

    print(f"Saving visualization to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print(f"Success! Open {OUTPUT_HTML} in your browser to view.")

if __name__ == "__main__":
    create_visualizations()

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Files
EDU_FILE = "opri_pivoted.csv"
OUTPUT_HTML = "out_of_school_analysis.html"

# Indicators
INDICATORS = {
    "Pop_Both": "School age population, primary education, both sexes (number)",
    "Pop_Female": "School age population, primary education, female (number)",
    "Pop_Male": "School age population, primary education, male (number)",
    "OOS_Both": "Out-of-school children of primary school age, both sexes (number)",
    "OOS_Female": "Out-of-school children of primary school age, female (number)",
    "OOS_Male": "Out-of-school children of primary school age, male (number)"
}

def create_oos_analysis():
    if not os.path.exists(EDU_FILE):
        print(f"Error: {EDU_FILE} not found.")
        return

    print("Loading Education Data...")
    df = pd.read_csv(EDU_FILE)
    
    # Filter for rows that have at least some population data or OOS data
    relevant_cols = list(INDICATORS.values()) + ["COUNTRY_NAME", "YEAR"]
    df_subset = df[relevant_cols].dropna(how='all', subset=list(INDICATORS.values()))
    
    countries = sorted(df_subset["COUNTRY_NAME"].unique())
    print(f"Found data for {len(countries)} countries.")

    # Create figure
    fig = go.Figure()

    country_traces = {}
    trace_idx = 0

    for country in countries:
        country_data = df_subset[df_subset["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # 1. Total Population (Both) - Area
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data[INDICATORS["Pop_Both"]],
            name="Total Primary Population", mode='lines',
            line=dict(width=0.5, color='lightgrey'),
            fill='toself', fillcolor='rgba(211, 211, 211, 0.3)',
            visible=False
        ))

        # 2. OOS Female - Bar
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_Female"]],
            name="Out-of-School (Female)",
            marker_color='rgba(255, 105, 180, 0.7)', # HotPink
            visible=False
        ))

        # 3. OOS Male - Bar
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_Male"]],
            name="Out-of-School (Male)",
            marker_color='rgba(30, 144, 255, 0.7)', # DodgerBlue
            visible=False
        ))

        # 4. Pop Female - Line (Reference)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data[INDICATORS["Pop_Female"]],
            name="Pop Female (Ref)", mode='lines',
            line=dict(width=2, color='rgba(255, 105, 180, 1)', dash='dot'),
            visible=False
        ))

        # 5. Pop Male - Line (Reference)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data[INDICATORS["Pop_Male"]],
            name="Pop Male (Ref)", mode='lines',
            line=dict(width=2, color='rgba(30, 144, 255, 1)', dash='dot'),
            visible=False
        ))

        country_traces[country] = list(range(trace_idx, trace_idx + 5))
        trace_idx += 5

    # Dropdown buttons
    buttons = []
    for country, indices in country_traces.items():
        visibility = [False] * len(fig.data)
        for idx in indices:
            visibility[idx] = True
            
        buttons.append(dict(
            label=country,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"Primary School-Age vs Out-of-School: {country}"}]
        ))

    # Set default
    if countries:
        first_country = countries[0]
        for idx in country_traces[first_country]:
            fig.data[idx].visible = True

    fig.update_layout(
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            x=0.1, xanchor="left", y=1.15, yanchor="top"
        )],
        title_text=f"Primary School-Age vs Out-of-School: {countries[0] if countries else 'N/A'}",
        xaxis=dict(title="Year", tickmode='linear', dtick=1),
        yaxis=dict(title="Number of Children"),
        template="plotly_white",
        barmode='group',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    print(f"Saving to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print("Success!")

if __name__ == "__main__":
    create_oos_analysis()

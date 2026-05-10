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

# Colors and Styling
PALETTE = {
    "Male": "#1CABE2",
    "Female": "#E83F6F",
    "Both": "#6A1E74",
    "Background": "#F7F4EF",
    "Text": "#1A1A2E",
    "Grey": "#6B7280"
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
            line=dict(width=0.5, color=PALETTE["Grey"]),
            fill='toself', fillcolor='rgba(107, 114, 128, 0.1)',
            visible=False,
            hoverinfo='skip'
        ))

        # 2. OOS Female - Bar
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_Female"]],
            name="Female Out-of-School",
            marker_color=PALETTE["Female"],
            opacity=0.8,
            visible=False
        ))

        # 3. OOS Male - Bar
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_Male"]],
            name="Male Out-of-School",
            marker_color=PALETTE["Male"],
            opacity=0.8,
            visible=False
        ))

        # 4. Pop Female - Line (Reference)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data[INDICATORS["Pop_Female"]],
            name="Female Pop (Ref)", mode='lines',
            line=dict(width=2, color=PALETTE["Female"], dash='dot'),
            visible=False
        ))

        # 5. Pop Male - Line (Reference)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data[INDICATORS["Pop_Male"]],
            name="Male Pop (Ref)", mode='lines',
            line=dict(width=2, color=PALETTE["Male"], dash='dot'),
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
            args=[{"visible": visibility}]
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
            x=0.0, xanchor="left", y=1.08, yanchor="top",
            font=dict(color=PALETTE["Text"]),
            bgcolor="white",
            bordercolor=PALETTE["Grey"]
        )],
        paper_bgcolor=PALETTE["Background"],
        plot_bgcolor=PALETTE["Background"],
        title=dict(
            text="National Profiles: Primary School-Age vs. Out-of-School Children",
            x=0.5,
            xanchor="center",
            font=dict(color=PALETTE["Text"], size=22)
        ),
        margin=dict(t=100, b=50, l=50, r=50),
        xaxis=dict(
            title="Year", 
            tickmode='linear', 
            dtick=1,
            color=PALETTE["Grey"],
            title_font=dict(color=PALETTE["Text"]),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title="Number of Children",
            color=PALETTE["Grey"],
            title_font=dict(color=PALETTE["Text"]),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        template="plotly_white",
        barmode='group',
        hovermode="x unified",
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color=PALETTE["Text"])
        )
    )

    print(f"Saving to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print("Success!")

if __name__ == "__main__":
    create_oos_analysis()

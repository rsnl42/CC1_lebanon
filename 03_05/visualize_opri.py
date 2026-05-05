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

import pandas as pd
import plotly.graph_objects as go
import os

INPUT_FILE = "opri_pivoted.csv"
OUTPUT_HTML = "education_trends.html"

# Key indicators we want to explore
INDICATORS = [
    "Gross enrolment ratio, primary, both sexes (%)",
    "Gross enrolment ratio, lower secondary, both sexes (%)",
    "Government expenditure on primary education as a percentage of GDP (%)"
]

# Colors and Styling
PALETTE = {
    "Background": "#F7F4EF",
    "Text": "#1A1A2E",
    "Grey": "#6B7280",
    "Accent1": "#0058A5", # Primary
    "Accent2": "#00833D", # Secondary
    "Accent3": "#E07B3B"  # Expenditure
}

def create_visualizations():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Loading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    available_indicators = [idx for idx in INDICATORS if idx in df.columns]
    if not available_indicators: return

    countries = sorted(df["COUNTRY_NAME"].unique())
    fig = go.Figure()

    country_traces = {}
    trace_idx = 0

    for country in countries:
        country_data = df[df["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # Add traces for each indicator
        for i, indicator in enumerate(available_indicators):
            color_key = f"Accent{i+1}"
            fig.add_trace(go.Scatter(
                x=country_data["YEAR"], y=country_data[indicator],
                name=indicator, mode='lines+markers',
                line=dict(width=3, color=PALETTE.get(color_key, "#333")),
                connectgaps=True,
                visible=False
            ))
        
        country_traces[country] = list(range(trace_idx, trace_idx + len(available_indicators)))
        trace_idx += len(available_indicators)

    buttons = []
    for country, indices in country_traces.items():
        visibility = [False] * len(fig.data)
        for idx in indices:
            visibility[idx] = True
        buttons.append(dict(label=country, method="update", args=[{"visible": visibility}]))

    if countries:
        for idx in country_traces[countries[0]]:
            fig.data[idx].visible = True

    fig.update_layout(
        updatemenus=[dict(
            active=0, buttons=buttons, direction="down",
            x=0.0, xanchor="left", y=1.1, yanchor="top",
            font=dict(color=PALETTE["Text"]),
            bgcolor="white", bordercolor=PALETTE["Grey"]
        )],
        paper_bgcolor=PALETTE["Background"],
        plot_bgcolor=PALETTE["Background"],
        title=dict(
            text="Macro Trends: Enrollment & Expenditure by Country",
            x=0.5, xanchor="center",
            font=dict(color=PALETTE["Text"], size=22)
        ),
        margin=dict(t=120, b=100, l=50, r=50),
        xaxis=dict(title="Year", color=PALETTE["Grey"], gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(title="Value (%)", color=PALETTE["Grey"], gridcolor='rgba(0,0,0,0.05)'),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.2, 
            xanchor="center", 
            x=0.5, 
            font=dict(color=PALETTE["Text"])
        )
    )

    print(f"Saving to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print("Success!")

if __name__ == "__main__":
    create_visualizations()

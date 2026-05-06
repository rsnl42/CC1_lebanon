import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Files
EDU_FILE = "opri_pivoted.csv"
CONFLICT_FILES = ["DATA/HRP_1_countries_geocoded.csv", "DATA/HRP_2_countries_geocoded.csv"]
OUTPUT_HTML = "conflict_edu_analysis.html"

# Key Indicators
# Gross enrolment ratio is more dense and provides better overlap
EDU_INDICATOR_1 = "Gross enrolment ratio, primary, both sexes (%)"
EDU_INDICATOR_2 = "Survival rate to the last grade of primary education, both sexes (%)"

# Colors and Styling
PALETTE = {
    "Male": "#1CABE2",
    "Female": "#E83F6F",
    "Both": "#6A1E74",
    "Background": "#F7F4EF",
    "Text": "#1A1A2E",
    "Grey": "#6B7280",
    "Fatalities": "#7B0000", # Catastrophe
    "Events": "#E07B3B",     # Crisis
    "Primary": "#0058A5",    # Primary school age
    "Secondary": "#00833D"   # Secondary school age
}

def cross_analyze():
    if not os.path.exists(EDU_FILE):
        print(f"Error: {EDU_FILE} not found.")
        return

    print("Loading Education Data...")
    edu_df = pd.read_csv(EDU_FILE)
    
    # Load and combine conflict data
    print("Loading Conflict Data...")
    conflict_list = []
    for f in CONFLICT_FILES:
        if os.path.exists(f):
            conflict_list.append(pd.read_csv(f))
    
    if not conflict_list:
        print("Error: No conflict data files found.")
        return
        
    conflict_df = pd.concat(conflict_list)
    
    # Aggregate conflict data by Country (ISO3) and Year
    print("Aggregating Conflict Data...")
    conflict_yearly = conflict_df.groupby(["Country", "Year"])[["Fatalities", "Events"]].sum().reset_index()
    conflict_yearly.rename(columns={"Country": "COUNTRY_NAME", "Year": "YEAR"}, inplace=True)
    conflict_yearly["YEAR"] = conflict_yearly["YEAR"].astype(int)

    # Use a left merge starting from conflict_yearly to ensure all conflict years are shown
    # even if education data is missing for those years.
    print("Merging Data...")
    merged = pd.merge(conflict_yearly, edu_df, on=["COUNTRY_NAME", "YEAR"], how="left")
    
    # We want to keep all years where there is conflict data
    countries = merged["COUNTRY_NAME"].unique()
    print(f"Found data for {len(countries)} countries.")

    # Load DVI stats
    dvi_df = pd.read_csv("country_dvi_stats.csv")
    dvi_df.rename(columns={"country": "COUNTRY_NAME", "year": "YEAR"}, inplace=True)
    merged = pd.merge(merged, dvi_df, on=["COUNTRY_NAME", "YEAR"], how="left")

    # Create the figure with three axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add a third y-axis for DVI
    
    
    
    

    # ... (rest of the trace-adding logic)
    country_traces = {}
    trace_idx = 0

    for country in sorted(countries):
        country_data = merged[merged["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # Education Line 1: Gross Enrolment
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"], 
                y=country_data[EDU_INDICATOR_1], 
                name="Gross Enrolment Ratio (%)", 
                mode='lines+markers',
                line=dict(width=3, color=PALETTE["Primary"]),
                connectgaps=True,
                visible=False,
                hovertemplate="GER: %{y:.2f}%<extra></extra>"
            ),
            secondary_y=False,
        )

        # DVI Trace
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"],
                y=country_data["DVI"],
                name="Dynamic Vulnerability Index (0-100)",
                mode='lines+markers',
                line=dict(width=2, color=PALETTE["Fatalities"]),
                visible=False,
                hovertemplate="DVI: %{y:.2f}<extra></extra>"
            ),
            secondary_y=True,
        )

        # Education Line 2: Survival Rate
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"], 
                y=country_data[EDU_INDICATOR_2], 
                name="Survival Rate (%)", 
                mode='lines+markers',
                line=dict(width=3, color=PALETTE["Secondary"], dash='dot'),
                connectgaps=True,
                visible=False,
                hovertemplate="Survival: %{y:.2f}%<extra></extra>"
            ),
            secondary_y=False,
        )
        
        # Conflict Bars (Fatalities)
        fig.add_trace(
            go.Bar(
                x=country_data["YEAR"], 
                y=country_data["Fatalities"], 
                name="Fatalities", 
                marker_color=PALETTE["Fatalities"],
                opacity=0.7,
                visible=False,
                hovertemplate="Fatalities: %{y:,.0f}<extra></extra>"
            ),
            secondary_y=True,
        )

        # Conflict Bars (Events)
        fig.add_trace(
            go.Bar(
                x=country_data["YEAR"], 
                y=country_data["Events"], 
                name="Events", 
                marker_color=PALETTE["Events"],
                opacity=0.7,
                visible=False,
                hovertemplate="Events: %{y:,.0f}<extra></extra>"
            ),
            secondary_y=True,
        )
        
        country_traces[country] = [trace_idx, trace_idx + 1, trace_idx + 2, trace_idx + 3, trace_idx + 4]
        trace_idx += 5

    # Create dropdown buttons
    buttons = []
    for country, indices in country_traces.items():
        # Create a visibility list where only this country's traces are True
        visibility = [False] * len(fig.data)
        for idx in indices:
            visibility[idx] = True
            
        buttons.append(dict(
            label=country,
            method="update",
            args=[{"visible": visibility}]
        ))

    # Set the first country as visible by default
    first_country = sorted(countries)[0]
    for idx in country_traces[first_country]:
        fig.data[idx].visible = True

    fig.update_layout(
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.0,
            xanchor="left",
            y=1.08,
            yanchor="top",
            font=dict(color=PALETTE["Text"]),
            bgcolor="white",
            bordercolor=PALETTE["Grey"]
        )],
        paper_bgcolor=PALETTE["Background"],
        plot_bgcolor=PALETTE["Background"],
        title=dict(
            text="Conflict Intensity vs. Education Metrics",
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
        template="plotly_white",
        hovermode="x unified",
        barmode='group',
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color=PALETTE["Text"])
        )
    )

    fig.update_yaxes(
        title_text="Education Metrics (%)", 
        secondary_y=False, 
        range=[0, 150],
        color=PALETTE["Grey"],
        title_font=dict(color=PALETTE["Text"]),
        gridcolor='rgba(0,0,0,0.05)',
        tickformat=".2f"
    )
    fig.update_yaxes(
        title_text="Conflict Metrics (Count)", 
        secondary_y=True,
        color=PALETTE["Grey"],
        title_font=dict(color=PALETTE["Text"]),
        showgrid=False,
        tickformat=","
    )

    print(f"Saving to {OUTPUT_HTML}...")
    html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    js_glossary = """
    <script>
    const glossary = {
        'Gross Enrolment Ratio (%)': 'Total enrollment in primary education regardless of age, as a % of the official primary school-age population.',
        'Survival Rate (%)': 'Percentage of students who are expected to reach the last grade of primary education.',
        'Fatalities': 'Total deaths resulting from conflict events.',
        'Events': 'Number of distinct conflict events (battles, explosions, etc.).'
    };
    function applyGlossary() {
        document.querySelectorAll('.legendtext').forEach(el => {
            const text = el.textContent.trim();
            if (glossary[text]) {
                el.setAttribute('title', glossary[text]);
                el.style.cursor = 'help';
            }
        });
    }
    setInterval(applyGlossary, 1000);
    </script>
    """
    with open(OUTPUT_HTML, "w") as f:
        f.write(html.replace('</body>', js_glossary + '</body>'))
    print("Success!")


if __name__ == "__main__":
    cross_analyze()

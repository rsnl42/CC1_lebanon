import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Files
EDU_FILE = "opri_pivoted.csv"
CONFLICT_FILES = ["DATA/HRP_1_countries_geocoded.csv", "DATA/HRP_2_countries_geocoded.csv"]
OUTPUT_HTML = "conflict_edu_gender_analysis.html"

# Indicators
INDICATORS = {
    "GER Female": "Gross enrolment ratio, primary, female (%)",
    "GER Male": "Gross enrolment ratio, primary, male (%)",
    "Survival Female": "Survival rate to the last grade of primary education, female (%)",
    "Survival Male": "Survival rate to the last grade of primary education, male (%)"
}

# Colors and Styling
PALETTE = {
    "Male": "#1CABE2",
    "Female": "#E83F6F",
    "Both": "#6A1E74",
    "Background": "#F7F4EF",
    "Text": "#1A1A2E",
    "Grey": "#6B7280",
    "Fatalities": "#7B0000", # Catastrophe
    "Events": "#E07B3B"       # Crisis
}

def create_gender_analysis():
    if not os.path.exists(EDU_FILE):
        print(f"Error: {EDU_FILE} not found.")
        return

    print("Loading Education Data...")
    edu_df = pd.read_csv(EDU_FILE)
    
    print("Loading Conflict Data...")
    conflict_list = []
    for f in CONFLICT_FILES:
        if os.path.exists(f):
            conflict_list.append(pd.read_csv(f))
    
    if not conflict_list:
        print("Error: No conflict data files found.")
        return
        
    conflict_df = pd.concat(conflict_list)
    
    print("Aggregating Conflict Data...")
    conflict_yearly = conflict_df.groupby(["Country", "Year"])[["Fatalities", "Events"]].sum().reset_index()
    conflict_yearly.rename(columns={"Country": "COUNTRY_NAME", "Year": "YEAR"}, inplace=True)
    conflict_yearly["YEAR"] = conflict_yearly["YEAR"].astype(int)

    print("Merging Data...")
    merged = pd.merge(conflict_yearly, edu_df, on=["COUNTRY_NAME", "YEAR"], how="left")
    
    countries = merged["COUNTRY_NAME"].unique()
    print(f"Found data for {len(countries)} countries.")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    country_traces = {}
    trace_idx = 0

    for country in sorted(countries):
        country_data = merged[merged["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # 1. GER Female
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"], 
                y=country_data[INDICATORS["GER Female"]], 
                name="GER Female (%)", 
                mode='lines+markers',
                line=dict(width=2, color=PALETTE["Female"]),
                connectgaps=True,
                visible=False
            ),
            secondary_y=False,
        )

        # 2. GER Male
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"], 
                y=country_data[INDICATORS["GER Male"]], 
                name="GER Male (%)", 
                mode='lines+markers',
                line=dict(width=2, color=PALETTE["Male"], dash='dash'), 
                connectgaps=True,
                visible=False
            ),
            secondary_y=False,
        )

        # 3. Survival Female
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"], 
                y=country_data[INDICATORS["Survival Female"]], 
                name="Survival Female (%)", 
                mode='lines+markers',
                line=dict(width=3, color=PALETTE["Female"], dash='dot'),
                connectgaps=True,
                visible=False
            ),
            secondary_y=False,
        )

        # 4. Survival Male
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"], 
                y=country_data[INDICATORS["Survival Male"]], 
                name="Survival Male (%)", 
                mode='lines+markers',
                line=dict(width=3, color=PALETTE["Male"], dash='longdashdot'), 
                connectgaps=True,
                visible=False
            ),
            secondary_y=False,
        )
        
        # 5. Fatalities
        fig.add_trace(
            go.Bar(
                x=country_data["YEAR"], 
                y=country_data["Fatalities"], 
                name="Fatalities", 
                marker_color=PALETTE["Fatalities"],
                opacity=0.7,
                visible=False
            ),
            secondary_y=True,
        )

        # 6. Events
        fig.add_trace(
            go.Bar(
                x=country_data["YEAR"], 
                y=country_data["Events"], 
                name="Events", 
                marker_color=PALETTE["Events"],
                opacity=0.7,
                visible=False
            ),
            secondary_y=True,
        )
        
        country_traces[country] = list(range(trace_idx, trace_idx + 6))
        trace_idx += 6

    buttons = []
    for country, indices in country_traces.items():
        visibility = [False] * len(fig.data)
        for idx in indices:
            visibility[idx] = True
            
        buttons.append(dict(
            label=country,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"Gendered Conflict-Education Impact: {country}"}]
        ))

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
            x=0.1,
            xanchor="left",
            y=1.15,
            yanchor="top",
            font=dict(color=PALETTE["Text"])
        )],
        paper_bgcolor=PALETTE["Background"],
        plot_bgcolor=PALETTE["Background"],
        title_text=f"Gendered Conflict-Education Impact: {first_country}",
        title_font=dict(color=PALETTE["Text"], size=20),
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
        gridcolor='rgba(0,0,0,0.05)'
    )
    fig.update_yaxes(
        title_text="Conflict Metrics (Count)", 
        secondary_y=True,
        color=PALETTE["Grey"],
        title_font=dict(color=PALETTE["Text"]),
        showgrid=False
    )

    print(f"Saving to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print("Success!")

if __name__ == "__main__":
    create_gender_analysis()

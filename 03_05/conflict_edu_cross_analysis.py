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
EDU_INDICATOR = "Gross enrolment ratio, primary, both sexes (%)"

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

    # Create the figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Dictionary to keep track of trace indices for the dropdown
    country_traces = {}
    trace_idx = 0

    for country in sorted(countries):
        country_data = merged[merged["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # Education Line (might have NaNs, Plotly will handle gaps or we can connect them)
        fig.add_trace(
            go.Scatter(
                x=country_data["YEAR"], 
                y=country_data[EDU_INDICATOR], 
                name="Gross Enrolment Ratio (%)", 
                mode='lines+markers',
                line=dict(width=3, color='royalblue'),
                connectgaps=True, # Connect gaps in education data
                visible=False
            ),
            secondary_y=False,
        )
        
        # Conflict Bars (Fatalities)
        fig.add_trace(
            go.Bar(
                x=country_data["YEAR"], 
                y=country_data["Fatalities"], 
                name="Fatalities", 
                marker_color='crimson',
                opacity=0.7,
                visible=False
            ),
            secondary_y=True,
        )

        # Conflict Bars (Events)
        fig.add_trace(
            go.Bar(
                x=country_data["YEAR"], 
                y=country_data["Events"], 
                name="Events", 
                marker_color='orange',
                opacity=0.7,
                visible=False
            ),
            secondary_y=True,
        )
        
        country_traces[country] = [trace_idx, trace_idx + 1, trace_idx + 2]
        trace_idx += 3

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
            args=[{"visible": visibility},
                  {"title": f"Conflict Impact in {country}: Education Survival vs Conflict Events"}]
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
            x=0.1,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )],
        title_text=f"Conflict Impact in {first_country}: Education Survival vs Conflict Events",
        xaxis=dict(title="Year", tickmode='linear', dtick=1),
        template="plotly_white",
        hovermode="x unified",
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_yaxes(title_text="Edu Survival Rate (%)", secondary_y=False, range=[0, 110])
    fig.update_yaxes(title_text="Conflict Metrics (Count)", secondary_y=True)

    print(f"Saving to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print("Success!")


if __name__ == "__main__":
    cross_analyze()

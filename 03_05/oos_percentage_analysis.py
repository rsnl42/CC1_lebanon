import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Files
EDU_FILE = "opri_pivoted.csv"
OUTPUT_HTML = "out_of_school_percentage.html"

# Indicators
INDICATORS = {
    "Pop_P_Both": "School age population, primary education, both sexes (number)",
    "Pop_S_Both": "School age population, secondary education, both sexes (number)",
    "Pop_P_Female": "School age population, primary education, female (number)",
    "Pop_S_Female": "School age population, secondary education, female (number)",
    "Pop_P_Male": "School age population, primary education, male (number)",
    "Pop_S_Male": "School age population, secondary education, male (number)",
    "OOS_PS_Both": "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)",
    "OOS_PS_Female": "Out-of-school children, adolescents and youth of primary and secondary school age, female (number)",
    "OOS_PS_Male": "Out-of-school children, adolescents and youth of primary and secondary school age, male (number)"
}

# Colors and Styling
PALETTE = {
    "Male": "#1CABE2",
    "Female": "#E83F6F",
    "Both": "#6A1E74",
    "Background": "#F7F4EF",
    "Text": "#1A1A2E",
    "Grey": "#6B7280",
    "OOS": "#C0392B"
}

def create_oos_percentage_analysis():
    if not os.path.exists(EDU_FILE):
        print(f"Error: {EDU_FILE} not found.")
        return

    print("Loading Education Data...")
    df_raw = pd.read_csv(EDU_FILE)
    df = df_raw.copy() # Avoid fragmentation warnings
    
    # Pre-calculate combined populations
    df["Total_Pop_Both"] = df[INDICATORS["Pop_P_Both"]].fillna(0) + df[INDICATORS["Pop_S_Both"]].fillna(0)
    df["Total_Pop_Female"] = df[INDICATORS["Pop_P_Female"]].fillna(0) + df[INDICATORS["Pop_S_Female"]].fillna(0)
    df["Total_Pop_Male"] = df[INDICATORS["Pop_P_Male"]].fillna(0) + df[INDICATORS["Pop_S_Male"]].fillna(0)
    
    # Handle zeros where both were NaN
    mask_both = df[INDICATORS["Pop_P_Both"]].isna() & df[INDICATORS["Pop_S_Both"]].isna()
    df.loc[mask_both, "Total_Pop_Both"] = pd.NA
    
    # Calculate Percentages
    df["OOS_Rate_Both"] = (df[INDICATORS["OOS_PS_Both"]] / df["Total_Pop_Both"]) * 100
    df["OOS_Rate_Female"] = (df[INDICATORS["OOS_PS_Female"]] / df["Total_Pop_Female"]) * 100
    df["OOS_Rate_Male"] = (df[INDICATORS["OOS_PS_Male"]] / df["Total_Pop_Male"]) * 100

    relevant_cols = ["COUNTRY_NAME", "YEAR", "OOS_Rate_Both", "OOS_Rate_Female", "OOS_Rate_Male", INDICATORS["OOS_PS_Both"], "Total_Pop_Both"]
    # Relaxed filter: keep any row that has either OOS Rate OR Total Pop data
    df_subset = df[relevant_cols].dropna(how='all', subset=["OOS_Rate_Both", "Total_Pop_Both"])
    
    countries = sorted(df_subset["COUNTRY_NAME"].unique())
    print(f"Found data for {len(countries)} countries.")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    country_traces = {}
    trace_idx = 0

    for country in countries:
        country_data = df_subset[df_subset["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # 1. Total Pop (Area on Secondary Y)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["Total_Pop_Both"],
            name="Total School-Age Pop", mode='lines',
            line=dict(width=0.5, color=PALETTE["Grey"]),
            fill='toself', fillcolor='rgba(107, 114, 128, 0.1)', # Grey with opacity
            visible=False,
            hoverinfo='skip'
        ), secondary_y=True)

        # 2. OOS Rate (%) - Both (Main Line)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["OOS_Rate_Both"],
            name="Total OOS Rate (%)", mode='lines+markers',
            line=dict(width=4, color=PALETTE["Both"]),
            visible=False
        ), secondary_y=False)

        # 3. OOS Rate (%) - Female
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["OOS_Rate_Female"],
            name="Female OOS Rate (%)", mode='lines+markers',
            line=dict(width=2, color=PALETTE["Female"]),
            visible=False
        ), secondary_y=False)

        # 4. OOS Rate (%) - Male
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["OOS_Rate_Male"],
            name="Male OOS Rate (%)", mode='lines+markers',
            line=dict(width=2, color=PALETTE["Male"], dash='dash'),
            visible=False
        ), secondary_y=False)

        # 5. Total OOS Count (Bar for context on Secondary Y)
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_PS_Both"]],
            name="Total OOS Count",
            marker_color=PALETTE["OOS"],
            opacity=0.4,
            visible=False
        ), secondary_y=True)

        country_traces[country] = list(range(trace_idx, trace_idx + 5))
        trace_idx += 5

    buttons = []
    for country, indices in country_traces.items():
        visibility = [False] * len(fig.data)
        for idx in indices:
            visibility[idx] = True
            
        buttons.append(dict(
            label=country,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"Out-of-School Analysis: {country}"}]
        ))

    if countries:
        for idx in country_traces[countries[0]]:
            fig.data[idx].visible = True

    fig.update_layout(
        updatemenus=[dict(
            active=0, buttons=buttons, direction="down",
            x=0.0, xanchor="left", y=1.08, yanchor="top",
            font=dict(color=PALETTE["Text"]),
            bgcolor="white",
            bordercolor=PALETTE["Grey"]
        )],
        paper_bgcolor=PALETTE["Background"],
        plot_bgcolor=PALETTE["Background"],
        title=dict(
            text=f"Out-of-School Analysis: {countries[0] if countries else 'N/A'}",
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
            title="Out-of-School Rate (%)", 
            range=[0, 105],
            color=PALETTE["Grey"],
            title_font=dict(color=PALETTE["Text"]),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis2=dict(
            title="Absolute Counts", 
            overlaying='y', 
            side='right', 
            showgrid=False,
            color=PALETTE["Grey"],
            title_font=dict(color=PALETTE["Text"])
        ),
        template="plotly_white",
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
    create_oos_percentage_analysis()

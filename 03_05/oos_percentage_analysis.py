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

def create_oos_percentage_analysis():
    if not os.path.exists(EDU_FILE):
        print(f"Error: {EDU_FILE} not found.")
        return

    print("Loading Education Data...")
    df = pd.read_csv(EDU_FILE)
    
    # Pre-calculate combined populations
    df["Total_Pop_Both"] = df[INDICATORS["Pop_P_Both"]].fillna(0) + df[INDICATORS["Pop_S_Both"]].fillna(0)
    df["Total_Pop_Female"] = df[INDICATORS["Pop_P_Female"]].fillna(0) + df[INDICATORS["Pop_S_Female"]].fillna(0)
    df["Total_Pop_Male"] = df[INDICATORS["Pop_P_Male"]].fillna(0) + df[INDICATORS["Pop_S_Male"]].fillna(0)
    
    # Handle zeros where both were NaN
    mask_both = df[INDICATORS["Pop_P_Both"]].isna() & df[INDICATORS["Pop_S_Both"]].isna()
    df.loc[mask_both, "Total_Pop_Both"] = pd.NA
    
    # Calculate Percentages
    # Rate (%) = (OOS Number / Total Pop) * 100
    df["OOS_Rate_Both"] = (df[INDICATORS["OOS_PS_Both"]] / df["Total_Pop_Both"]) * 100
    df["OOS_Rate_Female"] = (df[INDICATORS["OOS_PS_Female"]] / df["Total_Pop_Female"]) * 100
    df["OOS_Rate_Male"] = (df[INDICATORS["OOS_PS_Male"]] / df["Total_Pop_Male"]) * 100

    relevant_cols = ["COUNTRY_NAME", "YEAR", "OOS_Rate_Both", "OOS_Rate_Female", "OOS_Rate_Male", INDICATORS["OOS_PS_Both"]]
    df_subset = df[relevant_cols].dropna(subset=["OOS_Rate_Both"])
    
    countries = sorted(df_subset["COUNTRY_NAME"].unique())
    print(f"Found data for {len(countries)} countries.")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    country_traces = {}
    trace_idx = 0

    for country in countries:
        country_data = df_subset[df_subset["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # 1. OOS Rate (%) - Both (Main Line)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["OOS_Rate_Both"],
            name="Out-of-School Rate (%)", mode='lines+markers',
            line=dict(width=4, color='black'),
            visible=False
        ), secondary_y=False)

        # 2. OOS Rate (%) - Female
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["OOS_Rate_Female"],
            name="Female OOS Rate (%)", mode='lines+markers',
            line=dict(width=2, color='rgba(255, 20, 147, 1)'), # DeepPink
            visible=False
        ), secondary_y=False)

        # 3. OOS Rate (%) - Male
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["OOS_Rate_Male"],
            name="Male OOS Rate (%)", mode='lines+markers',
            line=dict(width=2, color='rgba(0, 191, 255, 1)', dash='dash'), # DeepSkyBlue
            visible=False
        ), secondary_y=False)

        # 4. Total OOS Count (Bar for context)
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_PS_Both"]],
            name="Total OOS Count",
            marker_color='rgba(200, 200, 200, 0.4)',
            visible=False
        ), secondary_y=True)

        country_traces[country] = [trace_idx, trace_idx + 1, trace_idx + 2, trace_idx + 3]
        trace_idx += 4

    # Dropdown
    buttons = []
    for country, indices in country_traces.items():
        visibility = [False] * len(fig.data)
        for idx in indices:
            visibility[idx] = True
            
        buttons.append(dict(
            label=country,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"Out-of-School Rate (%): {country}"}]
        ))

    if countries:
        for idx in country_traces[countries[0]]:
            fig.data[idx].visible = True

    fig.update_layout(
        updatemenus=[dict(
            active=0, buttons=buttons, direction="down",
            x=0.1, xanchor="left", y=1.15, yanchor="top"
        )],
        title_text=f"Out-of-School Rate (%): {countries[0] if countries else 'N/A'}",
        xaxis=dict(title="Year", tickmode='linear', dtick=1),
        yaxis=dict(title="Out-of-School Rate (%)", range=[0, 100]),
        yaxis2=dict(title="Absolute OOS Count", overlaying='y', side='right', showgrid=False),
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    print(f"Saving to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print("Success!")

if __name__ == "__main__":
    create_oos_percentage_analysis()

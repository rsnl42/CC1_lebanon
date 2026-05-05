import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Files
EDU_FILE = "opri_pivoted.csv"
OUTPUT_HTML = "oos_profile.html"

# Indicators
INDICATORS = {
    "Pop_P": "School age population, primary education, both sexes (number)",
    "Pop_S": "School age population, secondary education, both sexes (number)",
    "Pop_PF": "School age population, primary education, female (number)",
    "Pop_SF": "School age population, secondary education, female (number)",
    "Pop_PM": "School age population, primary education, male (number)",
    "Pop_SM": "School age population, secondary education, male (number)",
    "OOS_PS": "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)",
    "OOS_F": "Out-of-school children, adolescents and youth of primary and secondary school age, female (number)",
    "OOS_M": "Out-of-school children, adolescents and youth of primary and secondary school age, male (number)"
}

# Colors
PALETTE = {
    "Male": "#1CABE2",
    "Female": "#E83F6F",
    "Both": "#6A1E74",
    "Background": "#F7F4EF",
    "Text": "#1A1A2E",
    "Grey": "#6B7280",
    "OOS": "#C0392B"
}

def create_comprehensive_oos():
    if not os.path.exists(EDU_FILE):
        print(f"Error: {EDU_FILE} not found.")
        return

    print("Loading Education Data...")
    df = pd.read_csv(EDU_FILE)
    
    # Pre-calculate Combined Metrics
    df["Total_Pop"] = df[INDICATORS["Pop_P"]].fillna(0) + df[INDICATORS["Pop_S"]].fillna(0)
    df["Total_Pop_F"] = df[INDICATORS["Pop_PF"]].fillna(0) + df[INDICATORS["Pop_SF"]].fillna(0)
    df["Total_Pop_M"] = df[INDICATORS["Pop_PM"]].fillna(0) + df[INDICATORS["Pop_SM"]].fillna(0)
    
    # Calculate Rates with rounding
    df["OOS_Rate"] = ((df[INDICATORS["OOS_PS"]] / df["Total_Pop"]) * 100).round(2)
    df["OOS_Rate_F"] = ((df[INDICATORS["OOS_F"]] / df["Total_Pop_F"]) * 100).round(2)
    df["OOS_Rate_M"] = ((df[INDICATORS["OOS_M"]] / df["Total_Pop_M"]) * 100).round(2)

    # Subset to countries with at least some data
    relevant_cols = ["COUNTRY_NAME", "YEAR", "Total_Pop", INDICATORS["OOS_PS"], INDICATORS["OOS_F"], INDICATORS["OOS_M"], "OOS_Rate", "OOS_Rate_F", "OOS_Rate_M"]
    df_subset = df[relevant_cols].dropna(subset=["Total_Pop", INDICATORS["OOS_PS"]], how='all')
    
    countries = sorted(df_subset["COUNTRY_NAME"].unique())
    print(f"Found data for {len(countries)} countries.")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    country_traces = {}
    trace_idx = 0

    for country in countries:
        c_data = df_subset[df_subset["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # 1. Total Population (Area)
        fig.add_trace(go.Scatter(
            x=c_data["YEAR"], y=c_data["Total_Pop"],
            name="Total Pop", mode='lines',
            line=dict(width=0.5, color=PALETTE["Grey"]),
            fill='toself', fillcolor='rgba(107, 114, 128, 0.05)',
            visible=False, hoverinfo='skip'
        ), secondary_y=False)

        # 2. OOS Bars
        fig.add_trace(go.Bar(
            x=c_data["YEAR"], y=c_data[INDICATORS["OOS_F"]],
            name="Female OOS", marker_color=PALETTE["Female"],
            opacity=0.4, visible=False,
            hovertemplate="Female OOS: %{y:,.2f}<extra></extra>"
        ), secondary_y=False)

        fig.add_trace(go.Bar(
            x=c_data["YEAR"], y=c_data[INDICATORS["OOS_M"]],
            name="Male OOS", marker_color=PALETTE["Male"],
            opacity=0.4, visible=False,
            hovertemplate="Male OOS: %{y:,.2f}<extra></extra>"
        ), secondary_y=False)

        # 3. OOS Rates (Lines)
        fig.add_trace(go.Scatter(
            x=c_data["YEAR"], y=c_data["OOS_Rate"],
            name="Total OOS Rate (%)", mode='lines+markers',
            line=dict(width=4, color=PALETTE["Both"]),
            visible=False,
            hovertemplate="Total Rate: %{y:.2f}%<extra></extra>"
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x=c_data["YEAR"], y=c_data["OOS_Rate_F"],
            name="Female OOS Rate (%)", mode='lines+markers',
            line=dict(width=2, color=PALETTE["Female"]),
            visible=False,
            hovertemplate="Female Rate: %{y:.2f}%<extra></extra>"
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x=c_data["YEAR"], y=c_data["OOS_Rate_M"],
            name="Male OOS Rate (%)", mode='lines+markers',
            line=dict(width=2, color=PALETTE["Male"], dash='dash'),
            visible=False,
            hovertemplate="Male Rate: %{y:.2f}%<extra></extra>"
        ), secondary_y=True)

        country_traces[country] = list(range(trace_idx, trace_idx + 6))
        trace_idx += 6

    # Dropdown
    buttons = []
    for country, indices in country_traces.items():
        visibility = [False] * len(fig.data)
        for idx in indices: visibility[idx] = True
        buttons.append(dict(label=country, method="update", args=[{"visible": visibility}]))

    if countries:
        for idx in country_traces[countries[0]]: fig.data[idx].visible = True

    fig.update_layout(
        updatemenus=[dict(
            active=0, buttons=buttons, direction="down",
            x=0.0, xanchor="left", y=1.1, yanchor="top",
            font=dict(color=PALETTE["Text"]), bgcolor="white", bordercolor=PALETTE["Grey"]
        )],
        paper_bgcolor=PALETTE["Background"],
        plot_bgcolor=PALETTE["Background"],
        title=dict(
            text="Comprehensive OOS Profile: Gendered Trends & Scale",
            x=0.5, xanchor="center", font=dict(color=PALETTE["Text"], size=22)
        ),
        margin=dict(t=120, b=50, l=50, r=50),
        xaxis=dict(title="Year", tickmode='linear', dtick=1, color=PALETTE["Grey"], gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(
            title="Number of Children (Absolute)", 
            color=PALETTE["Grey"], 
            gridcolor='rgba(0,0,0,0.05)',
            tickformat=".2f"
        ),
        yaxis2=dict(
            title="Out-of-School Rate (%)", 
            range=[0, 105], 
            overlaying='y', 
            side='right', 
            showgrid=False, 
            color=PALETTE["Both"],
            tickformat=".2f"
        ),
        template="plotly_white",
        barmode='group',
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=PALETTE["Text"]))
    )

    print(f"Saving to {OUTPUT_HTML}...")
    fig.write_html(OUTPUT_HTML)
    print("Success!")

if __name__ == "__main__":
    create_comprehensive_oos()

import pandas as pd
import plotly.graph_objects as go
import os

# Files
EDU_FILE = "opri_pivoted.csv"
OUTPUT_HTML = "out_of_school_analysis_v2.html"

# Indicators
INDICATORS = {
    "Pop_P_Both": "School age population, primary education, both sexes (number)",
    "Pop_S_Both": "School age population, secondary education, both sexes (number)",
    "OOS_PS_Both": "Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)",
    "OOS_PS_Female": "Out-of-school children, adolescents and youth of primary and secondary school age, female (number)",
    "OOS_PS_Male": "Out-of-school children, adolescents and youth of primary and secondary school age, male (number)"
}

def create_oos_analysis_v2():
    if not os.path.exists(EDU_FILE):
        print(f"Error: {EDU_FILE} not found.")
        return

    print("Loading Education Data...")
    df = pd.read_csv(EDU_FILE)
    
    # Calculate Total School Age Pop (Primary + Secondary)
    df["Total_Pop_PS"] = df[INDICATORS["Pop_P_Both"]].fillna(0) + df[INDICATORS["Pop_S_Both"]].fillna(0)
    # If both were NaN, the sum is 0, let's turn it back to NaN if appropriate
    mask = df[INDICATORS["Pop_P_Both"]].isna() & df[INDICATORS["Pop_S_Both"]].isna()
    df.loc[mask, "Total_Pop_PS"] = pd.NA

    relevant_cols = list(INDICATORS.values()) + ["COUNTRY_NAME", "YEAR", "Total_Pop_PS"]
    df_subset = df[relevant_cols].dropna(how='all', subset=[INDICATORS["OOS_PS_Both"], "Total_Pop_PS"])
    
    countries = sorted(df_subset["COUNTRY_NAME"].unique())
    print(f"Found data for {len(countries)} countries.")

    fig = go.Figure()

    country_traces = {}
    trace_idx = 0

    for country in countries:
        country_data = df_subset[df_subset["COUNTRY_NAME"] == country].sort_values("YEAR")
        
        # 1. Total Population (Area)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data["Total_Pop_PS"],
            name="Total School-Age Pop (P+S)", mode='lines',
            line=dict(width=0.5, color='rgba(200, 200, 200, 0.5)'),
            fill='toself', fillcolor='rgba(200, 200, 200, 0.2)',
            visible=False
        ))

        # 2. Total Out-of-School (Line)
        fig.add_trace(go.Scatter(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_PS_Both"]],
            name="Total Out-of-School", mode='lines+markers',
            line=dict(width=3, color='black'),
            visible=False
        ))

        # 3. OOS Female (Bar)
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_PS_Female"]],
            name="OOS Female (P+S)",
            marker_color='rgba(255, 20, 147, 0.7)', # DeepPink
            visible=False
        ))

        # 4. OOS Male (Bar)
        fig.add_trace(go.Bar(
            x=country_data["YEAR"], y=country_data[INDICATORS["OOS_PS_Male"]],
            name="OOS Male (P+S)",
            marker_color='rgba(0, 191, 255, 0.7)', # DeepSkyBlue
            visible=False
        ))

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
                  {"title": f"School-Age Pop vs Out-of-School (P+S): {country}"}]
        ))

    if countries:
        for idx in country_traces[countries[0]]:
            fig.data[idx].visible = True

    fig.update_layout(
        updatemenus=[dict(
            active=0, buttons=buttons, direction="down",
            x=0.1, xanchor="left", y=1.15, yanchor="top"
        )],
        title_text=f"School-Age Pop vs Out-of-School (P+S): {countries[0] if countries else 'N/A'}",
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
    create_oos_analysis_v2()

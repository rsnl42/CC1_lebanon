import pandas as pd
import matplotlib.pyplot as plt

# Load merged data
df = pd.read_csv("May_02/conflict_sfp_merged.csv")

# Filter for conflict-affected countries (Fatalities > 0)
conflict_df = df[df['Fatalities'] > 0].copy()

# Function to check for attendance impact in descriptions
def check_attendance_impact(text):
    if pd.isna(text): return "No Data"
    text = text.lower()
    keywords = ["attendance", "enrollment", "dropout", "fréquentation", "réguliers", "assiduité", "scolarisation", "absences"]
    if any(k in text for k in keywords):
        return "Reported Improvement"
    return "No Mention"

conflict_df['Attendance_Impact'] = conflict_df['Describe impacts of school feeding on students'].apply(check_attendance_impact)

# Sort by fatalities for better visualization
conflict_df = conflict_df.sort_values('Fatalities', ascending=True)

# Plotting
plt.figure(figsize=(12, 8))

# Define colors based on impact
colors = {
    "Reported Improvement": "forestgreen",
    "No Mention": "goldenrod",
    "No Data": "lightgray"
}
bar_colors = [colors[impact] for impact in conflict_df['Attendance_Impact']]

bars = plt.barh(conflict_df['country_name'], conflict_df['Fatalities'], color=bar_colors)

# Add Legend
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], color='forestgreen', lw=4, label='Reported Attendance Improvement'),
                   Line2D([0], [0], color='goldenrod', lw=4, label='Program Exists (No Impact Mentioned)'),
                   Line2D([0], [0], color='lightgray', lw=4, label='No Impact Data Available')]
plt.legend(handles=legend_elements, loc='lower right')

plt.title("Conflict Intensity (Fatalities) vs School Meal Impact on Attendance", fontsize=15)
plt.xlabel("Total Conflict Fatalities (Aggregated)", fontsize=12)
plt.ylabel("Country", fontsize=12)

# Add coverage annotations
for i, bar in enumerate(bars):
    coverage = conflict_df.iloc[i]['pct_coverage']
    if not pd.isna(coverage):
        plt.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2, f"Coverage: {coverage:.1f}%", va='center', fontsize=9)

plt.tight_layout()
plt.savefig("May_02/conflict_impact_chart.png")
print("Chart saved to May_02/conflict_impact_chart.png")

# Save the final analysis table
analysis_cols = [
    'country_name', 'Fatalities', 'pct_coverage', 
    'Is student attendance recorded?', 
    'Can individual students who received school feeding be linked to attendance?',
    'Attendance_Impact'
]
conflict_df[analysis_cols].to_csv("May_02/conflict_attendance_analysis.csv", index=False)
print("Analysis table saved to May_02/conflict_attendance_analysis.csv")

# Display a summary table
print("\n--- Conflict Zone Analysis Summary ---")
print(conflict_df[analysis_cols].to_string())

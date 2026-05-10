import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_dual_axis_chart(csv_path, output_path):
    # Load the data
    df = pd.read_csv(csv_path)

    # Filter for the two indicators we want to compare
    # 1. Total Refugees (UNHCR)
    # 2. Primary Enrollment Rate (World Bank)
    refugee_code = 'UNHCR_ALL_REFUGEES_LBN'
    enrollment_code = 'SE.PRM.ENRR'

    refugees = df[df['indicator_code'] == refugee_code].sort_values('year')
    enrollment = df[df['indicator_code'] == enrollment_code].sort_values('year')

    if refugees.empty or enrollment.empty:
        print("Error: Required indicators not found in CSV.")
        return

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Plot Refugee Count (Left Axis)
    color1 = '#dc2626' # Red
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total Refugees (Count)', color=color1, fontsize=12, fontweight='bold')
    line1 = ax1.plot(refugees['year'], refugees['value'], color=color1, marker='o', linewidth=3, label='Total Refugees')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)

    # Create a second axis for Enrollment
    ax2 = ax1.twinx()
    color2 = '#2563eb' # Blue
    ax2.set_ylabel('Primary Enrollment Rate (%)', color=color2, fontsize=12, fontweight='bold')
    line2 = ax2.plot(enrollment['year'], enrollment['value'], color=color2, marker='s', linewidth=3, label='Primary Enrollment (%)')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Add Breakpoints (Vertical Lines)
    breakpoints = [
        (2011, 'Syrian War'),
        (2019, 'Fin. Collapse'),
        (2020, 'Port Blast'),
    ]

    for year, label in breakpoints:
        plt.axvline(x=year, color='gray', linestyle='--', alpha=0.7)
        plt.text(year, ax2.get_ylim()[1] * 0.95, label, rotation=90, 
                 verticalalignment='top', fontsize=9, color='gray', fontweight='bold')

    # Title and Legend
    plt.title('Lebanon: Correlation between Refugee Influx and Primary Education Enrollment', 
              fontsize=14, pad=20, fontweight='bold')
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✅ Chart successfully saved to {output_path}")

if __name__ == "__main__":
    create_dual_axis_chart('lebanon_education_data.csv', 'crisis_correlation_chart.png')

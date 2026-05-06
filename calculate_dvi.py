import pandas as pd
import numpy as np
import os

def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

def calculate_dvi():
    # Load required data
    proximity_df = pd.read_csv('DATA/schools_proximity_analysis.csv')
    # Assuming school_vulnerability_count has the yearly stats
    vuln_df = pd.read_csv('school_vulnerability_count.csv')
    # OOS Data
    edu_df = pd.read_csv('opri_pivoted.csv')
    
    # 1. Proximity Pi: Normalized Vulnerable Schools Ratio
    vuln_df['Pi'] = normalize(vuln_df['vulnerable_percentage'])
    
    # 2. Fatality Intensity Ft: Placeholder for rolling sum of fatalities
    # In a full impl, this would read from conflict events; using vulnerability count as proxy if needed
    # Placeholder: Just use standardized vulnerable_schools as a proxy for intensity if fatality file isn't pre-aggregated
    vuln_df['Ft'] = normalize(vuln_df['vulnerable_schools'])
    
    # 3. Education Disruption Ed: Trend in OOS
    # Simplified: Annual % change
    edu_df = edu_df.sort_values(['COUNTRY_NAME', 'YEAR'])
    oos_col = 'Out-of-school children, adolescents and youth of primary and secondary school age, both sexes (number)'
    edu_df[oos_col] = pd.to_numeric(edu_df[oos_col], errors='coerce')
    edu_df['Ed'] = edu_df.groupby('COUNTRY_NAME')[oos_col].pct_change().fillna(0)
    edu_df['Ed'] = normalize(edu_df['Ed'])
    
    # Merge
    merged = vuln_df.merge(edu_df, left_on=['country', 'year'], right_on=['COUNTRY_NAME', 'YEAR'], how='left')
    
    # DVI Calculation with Fallbacks
    def compute_row(row):
        # Weights
        Wp, Wf, We = 0.3, 0.4, 0.3
        
        pi = row.get('Pi', 0)
        ft = row.get('Ft', 0)
        ed = row.get('Ed', 0)
        
        # Check availability
        available_count = sum([not np.isnan(pi), not np.isnan(ft), not np.isnan(ed)])
        
        if available_count == 3:
            score = (Wp * pi) + (Wf * ft) + (We * ed)
        else:
            # Simplified score logic
            score = (pi * 0.5) + (ft * 0.5)
            
        return round(score * 100, 2)
            
    merged['DVI'] = merged.apply(compute_row, axis=1)
    
    # Save output
    merged[['country', 'year', 'DVI']].to_csv('country_dvi_stats.csv', index=False)
    print("DVI calculation complete. Results saved to country_dvi_stats.csv")

if __name__ == "__main__":
    calculate_dvi()

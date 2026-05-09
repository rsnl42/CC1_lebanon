from long_data_engine import LongDataEngine

def calculate_transition_ratio(engine, primary_indicator, secondary_indicator, output_file):
    """
    Calculates transition ratio: Secondary_Enrollment / Primary_Enrollment_Previous_Year
    """
    # 1. Get filtered data
    pri = engine.get_indicator(primary_indicator)
    sec = engine.get_indicator(secondary_indicator)

    # 2. Rename value columns for clear merging
    pri = pri.rename(columns={'VALUE': 'pri_val'})
    sec = sec.rename(columns={'VALUE': 'sec_val'})

    # 3. Merge by Country and Year. 
    # Note: Transition usually happens from year X to X+1. 
    # We match secondary in year X with primary in year X-1.
    pri['YEAR'] = pri['YEAR'] + 1 
    merged = pri.merge(sec, on=['COUNTRY_NAME', 'YEAR'])

    # 4. Calculate ratio
    merged['ratio'] = merged['sec_val'] / merged['pri_val']

    # 5. Save
    merged.to_csv(output_file, index=False)
    print(f"Transition ratios saved to {output_file}")
    return merged

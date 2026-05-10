import sys
import os

# Add analysis_engine to sys.path so we can import modules
sys.path.append(os.path.abspath("analysis_engine"))

from long_data_engine import LongDataEngine
from transition_risk import calculate_transition_ratio

# 1. Initialize engine with mock data
engine = LongDataEngine("sandbox/mock_opri.csv")

# 2. Calculate transition ratios
result = calculate_transition_ratio(
    engine, 
    "Enrolment_Primary_Last_Grade", 
    "Enrolment_Lower_Secondary_First_Grade", 
    "outputs/test_transition_ratios.csv"
)

print("\nCalculation Results:")
print(result)

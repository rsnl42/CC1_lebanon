import pandas as pd
import sys
import os

sys.path.append(os.path.abspath("analysis_engine"))
from access_decay import AccessDecayEngine

# 1. Create Mock Data
schools = pd.DataFrame([
    {'school_id': 'S1', 'lat': 0.0, 'lon': 0.0}, # Close to conflict
    {'school_id': 'S2', 'lat': 5.0, 'lon': 5.0}  # Far from conflict
])

conflicts = pd.DataFrame([
    {'lat': 0.1, 'lon': 0.1, 'year': 2021, 'severity': 10},
    {'lat': 5.0, 'lon': 5.1, 'year': 2021, 'severity': 1}
])

# 2. Initialize Engine
engine = AccessDecayEngine(schools, conflicts)

# 3. Calculate Decay for 2021
results = engine.calculate_decay(year=2021, influence_radius=2.0)

print("Access Decay Results for 2021:")
print(results)

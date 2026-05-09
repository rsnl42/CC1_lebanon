import pandas as pd
import numpy as np

class AccessDecayEngine:
    def __init__(self, schools_df, conflict_df):
        """
        schools_df: ['school_id', 'lat', 'lon', 'region_id']
        conflict_df: ['lat', 'lon', 'year', 'severity']
        """
        self.schools = schools_df
        self.conflicts = conflict_df

    def calculate_decay(self, year, influence_radius=0.5):
        """
        Calculates the weighted distance decay for a specific year.
        'Cost' = Physical Distance + Sum(Conflict_Severity / distance_to_event)
        """
        results = []
        year_conflicts = self.conflicts[self.conflicts['year'] == year]
        
        for _, school in self.schools.iterrows():
            # Physical distance to target (simplified as 0 for this POC)
            base_cost = 0 
            
            # Conflict friction
            dist_to_conflicts = np.sqrt(
                (year_conflicts['lat'] - school['lat'])**2 + 
                (year_conflicts['lon'] - school['lon'])**2
            )
            
            # Apply friction: conflict severity weighted by inverse distance
            mask = dist_to_conflicts < influence_radius
            friction = (year_conflicts.loc[mask, 'severity'] / (dist_to_conflicts[mask] + 0.01)).sum()
            
            results.append({
                'school_id': school['school_id'],
                'access_score': base_cost + friction
            })
            
        return pd.DataFrame(results)

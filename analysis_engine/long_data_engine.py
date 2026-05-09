import pandas as pd

class LongDataEngine:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path, low_memory=False)

    def get_indicator(self, indicator_name):
        """Returns a filtered dataframe for a specific indicator name."""
        return self.df[self.df['INDICATOR_NAME'] == indicator_name][['COUNTRY_NAME', 'YEAR', 'VALUE']]

import pandas as pd

class region:
    def __init__(self, csv_folder=None, region_id=None):
        df_scalars = pd.read_csv(csv_folder)
        if region_id:
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)
        self.scalars = df_scalars
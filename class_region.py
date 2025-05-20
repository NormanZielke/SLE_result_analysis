import pandas as pd

from calc_results import(
    capacities_opt,
    cap_opt_bar
)

from plots import(
    barplot_c,
    barplot_e
)

class region:
    def __init__(self, csv_folder=None, region_id=None):
        df_scalars = pd.read_csv(csv_folder)
        if region_id:
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)
        self.scalars = df_scalars

    # Add functions

    capacities_opt = capacities_opt
    cap_opt_bar = cap_opt_bar
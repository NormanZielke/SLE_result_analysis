import pandas as pd

from calc_results import(
    capacities_opt,
    cap_opt_bar,
    dispatch_bar,
    plot_dir,
)


class region:
    def __init__(self,args, csv_folder=None, region_id=None):
        self.region_id = region_id
        df_scalars = pd.read_csv(csv_folder, sep=";")
        if region_id:
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)
        self.scalars = df_scalars

    # Add functions

    capacities_opt = capacities_opt
    cap_opt_bar = cap_opt_bar
    dispatch_bar = dispatch_bar
    #plot_dir = plot_dir
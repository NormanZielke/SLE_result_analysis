import pandas as pd

from calc_results import(
    capacities_opt,
    cap_opt_bar,
    dispatch_bar,
    techs_none

)

def read_csv_auto_sep(path):

    with open(path, 'r') as f:
        first_line = f.readline()
        if ";" in first_line:
            sep = ";"
        elif "," in first_line:
            sep = ","
        else:
            raise ValueError("Unbekannter CSV-Separator.")

    return pd.read_csv(path, sep=sep)

class region:
    def __init__(self,args, csv_folder=None, region_id=None):
        self.region_id = region_id
        df_scalars = read_csv_auto_sep(csv_folder)
        if region_id:
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)
        self.scalars = df_scalars

    # Add functions

    capacities_opt = capacities_opt
    cap_opt_bar = cap_opt_bar
    dispatch_bar = dispatch_bar
    techs_none = techs_none
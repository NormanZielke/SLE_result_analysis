import pandas as pd
import os

from calc_results import(
    capacities_opt,
    cap_opt_bar,
    dispatch_bar,
    techs_none,
    import_pie,
    generation_pie_electricty,
    generation_heat_high,
    generation_heat_low_central,
    generation_heat_low_decentral
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
    def __init__(self,args, csv_folder=None, region_id=None, from_combined_file=False):
        df_scalars = read_csv_auto_sep(csv_folder)
        self.region_id = region_id
        self.from_combined_file = from_combined_file

        if from_combined_file:
            df_scalars = df_scalars[df_scalars["name"].str.startswith(f"{region_id}-")].copy()
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)
        else:
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)

        self.scalars = df_scalars

    def get_results_path(self, filename):
        base_folder = "01_ALL_REGIONS" if self.from_combined_file else "Single_Regions"
        return os.path.join("results", base_folder, self.region_id, filename)


    # Add functions

    capacities_opt = capacities_opt

    cap_opt_bar = cap_opt_bar

    dispatch_bar = dispatch_bar

    techs_none = techs_none

    import_pie = import_pie

    generation_pie_electricity = generation_pie_electricty

    generation_heat_high = generation_heat_high

    generation_heat_low_central = generation_heat_low_central

    generation_heat_low_decentral = generation_heat_low_decentral
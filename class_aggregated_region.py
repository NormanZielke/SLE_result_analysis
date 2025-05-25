import os
import pandas as pd
from class_region import read_csv_auto_sep

from calc_results import (
    capacities_opt,
    cap_opt_bar,
    dispatch_bar,
    techs_none,
    import_pie,
    generation_pie_electricity,
    generation_heat_high,
    generation_heat_low_central,
    generation_heat_low_decentral
)

class aggregated_region:
    def __init__(self, region_id, csv_paths, output_folder):
        self.region_id = region_id
        self.output_folder = output_folder

        # Einlesen und zusammenführen
        if isinstance(csv_paths, str):
            df = read_csv_auto_sep(csv_paths)
        elif isinstance(csv_paths, list):
            df_list = [read_csv_auto_sep(p) for p in csv_paths]
            df = pd.concat(df_list, ignore_index=True)
        else:
            raise ValueError("csv_paths muss str oder list sein")

        # Region-Präfix entfernen
        df["name"] = df["name"].str.replace(r"^r\d{12}-", "", regex=True)

        # Gruppieren nach name UND var_name
        df_grouped = df.groupby(["name", "var_name"], as_index=False)["var_value"].sum()

        self.scalars = df_grouped

    def get_results_path(self, filename):
        return os.path.join(self.output_folder, filename)

    # Bestehende Methoden weiterverwenden
    capacities_opt = capacities_opt
    cap_opt_bar = cap_opt_bar
    dispatch_bar = dispatch_bar
    techs_none = techs_none
    import_pie = import_pie
    generation_pie_electricity = generation_pie_electricity
    generation_heat_high = generation_heat_high
    generation_heat_low_central = generation_heat_low_central
    generation_heat_low_decentral = generation_heat_low_decentral
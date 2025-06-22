import pandas as pd
import os
import yaml

from calc_results import(
    capacities_opt,
    cap_opt_bar,
    dispatch_bar,
    techs_none,
    import_pie,
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

def load_label_mapping(yaml_path="de.yml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        mapping = yaml.safe_load(f)
    return mapping

def apply_label_mapping(df, mapping, column="name"):
    df[column] = df[column].map(mapping).fillna(df[column])
    return df

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

        # 🔁 Lade Mapping und wende es an
        mapping = load_label_mapping("de.yml")
        df_scalars = apply_label_mapping(df_scalars, mapping)

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
    generation_heat_high = generation_heat_high
    generation_heat_low_central = generation_heat_low_central
    generation_heat_low_decentral = generation_heat_low_decentral
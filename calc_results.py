from plots import(
    barplot_c,
    barplot_e
)
import os

import pandas as pd



def capacities_opt(region):
    df_capacities = region.scalars[region.scalars["var_name"].str.startswith("invest_out")]
    df_cap_opt = df_capacities[df_capacities["var_value"] != 0]

    return df_cap_opt


def dispatch_elec(region):
    df_dispatch_elec = region.scalars[region.scalars.var_name == "flow_out_electricity"]
    df_dispatch_elec = df_dispatch_elec[df_dispatch_elec.var_value != 0]

    return df_dispatch_elec


def cap_opt_bar(region):

    df_cap_opt = capacities_opt(region)
    # Direction for bar-plot
    region_id = region.region_id
    filename = os.path.join("plots", region_id, f"capacities_opt_{region_id}.png")

    barplot_c(df_cap_opt,
              title = f"Optimierte Kapazitäten {region.region_id}",
              filename = filename)


def dispatch_bar(region):

    df_dispatch_elec = dispatch_elec(region)
    df_dispatch_elec.var_value *= 1e-3
    # Direction for bar-plot
    region_id = region.region_id
    filename = os.path.join("plots", region_id, f"dispatch_elec_{region_id}.png")

    barplot_e(df_dispatch_elec,
              title= f"Stromversorgung je Technologie {region.region_id}",
              filename = filename
              )

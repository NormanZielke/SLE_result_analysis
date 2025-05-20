from plots import(
    barplot_c
)

import pandas as pd


def capacities_opt(region):
    df_capacities = region.scalars[region.scalars["var_name"].str.startswith("invest_out")]
    df_cap_opt = df_capacities[df_capacities["var_value"] != 0]

    return df_cap_opt

def cap_opt_bar(region):
    df_cap_opt = capacities_opt(region)

    barplot_c(df_cap_opt,
              title = "Optimierte Kapazitäten",
              filename = "capacities_opt.png")

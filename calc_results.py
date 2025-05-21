from plots import(
    barplot_c,
    barplot_e,
    plot_pie,
    plot_pie_2,
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


def techs_none(region):
    df_capacities = region.scalars[region.scalars["var_name"].str.startswith("invest_out")]
    df_cap_none = df_capacities[df_capacities["var_value"] == 0]
    techs_none = df_cap_none.name.unique()

    region_id = region.region_id

    df_none = pd.DataFrame(techs_none, columns=[f"techs_none_{region_id}"])

    output_path = os.path.join("results", region_id, f"{region_id}_nicht_verwendete_technologien.csv")
    df_none.to_csv(output_path, index=True)


def cap_opt_bar(region):

    df_cap_opt = capacities_opt(region)
    # Direction for bar-plot
    region_id = region.region_id
    filename = os.path.join("results", region_id, f"{region_id}_capacities_opt.png")

    barplot_c(df_cap_opt,
              title = f"Optimierte Kapazitäten {region.region_id}",
              filename = filename)


def dispatch_bar(region):

    df_dispatch_elec = dispatch_elec(region)
    df_dispatch_elec.var_value *= 1e-3
    # Direction for bar-plot
    region_id = region.region_id
    filename = os.path.join("results", region_id, f"{region_id}_dispatch_elec.png")

    barplot_e(df_dispatch_elec,
              unit = "GWh",
              title= f"Stromversorgung je Technologie {region.region_id}",
              filename = filename
              )

def import_pie(region):
    df_dispatch_elec = dispatch_elec(region)
    # df Eigenerzeugung
    df_gen_elec = df_dispatch_elec[~df_dispatch_elec["name"].str.contains("electricity-import")]
    # df für Kreisdiagramm
    strom_eigenversorgung = df_gen_elec.var_value.sum() * 1e-3
    strom_import = df_dispatch_elec[df_dispatch_elec["name"] == "electricity-import"].var_value.sum() * 1e-3
    df_summary = pd.DataFrame({
        "var_value": [strom_eigenversorgung, strom_import]
    }, index=["Eigenerzeugung aus EE", "Strom_Import"])

    # Direction for bar-plot
    region_id = region.region_id
    filename = os.path.join("results", region_id, f"{region_id}_pie_import.png")

    plot_pie(labels = df_summary.index.tolist(),
             values = df_summary["var_value"].tolist(),
             title= f"Eigenerzeugung/Stromimporte {region.region_id}",
             filename = filename)

def generation_pie_electricty(region):
    df_dispatch_elec = dispatch_elec(region)
    # df Eigenerzeugung
    df_gen_elec = df_dispatch_elec[~df_dispatch_elec["name"].str.contains("electricity-import")].copy()
    df_gen_elec.var_value *= 1e-3

    # Direction for bar-plot
    region_id = region.region_id
    filename1 = os.path.join("results", region_id, f"{region_id}_electricty_bar.png")
    filename = os.path.join("results", region_id, f"{region_id}_electricty_pie.png")

    barplot_e(df_gen_elec,
              unit = "GWh",
              title= f"Anteil pro Technologie an Stromerzeugung {region.region_id}",
              filename = filename1
              )

    plot_pie_2(labels = df_gen_elec.name.tolist(),
             values = df_gen_elec.var_value.tolist(),
             title = f"Anteil pro Technologie an Stromerzeugung {region.region_id}",
             filename = filename
             )
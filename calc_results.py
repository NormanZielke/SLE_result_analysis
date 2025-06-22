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

    output_path = region.get_results_path(filename= f"{region_id}_nicht_verwendete_technologien.csv")
    df_none.to_csv(output_path, index=True)


def cap_opt_bar(region):
    df_cap_opt = capacities_opt(region)

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename = region.get_results_path(filename=f"{key}_capacities_opt.png")

    barplot_c(df_cap_opt,
              title=f"Optimierte Kapazitäten {region_label}",
              filename=filename)


def dispatch_bar(region):
    df_dispatch_elec = dispatch_elec(region)
    df_dispatch_elec.var_value *= 1e-3

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_dispatch_elec_bar.png")
    filename = region.get_results_path(filename=f"{key}_dispatch_elec_pie.png")


    barplot_e(df_dispatch_elec,
              unit="GWh",
              title=f"Stromversorgung je Technologie {region_label}",
              filename=filename1)

    plot_pie_2(labels=df_dispatch_elec.name.tolist(),
               values=df_dispatch_elec.var_value.tolist(),
               title=f"Anteil pro Technologie an Stromversorgung {region_label}",
               filename=filename)


def import_pie(region):
    df_dispatch_elec = dispatch_elec(region)
    # df Eigenerzeugung
    df_gen_elec = df_dispatch_elec[~df_dispatch_elec["name"].str.contains("Stromimport")]
    # df für Kreisdiagramm
    strom_eigenversorgung = df_gen_elec.var_value.sum() * 1e-3
    strom_import = df_dispatch_elec[df_dispatch_elec["name"] == "Stromimport"].var_value.sum() * 1e-3

    df_summary = pd.DataFrame({
        "var_value": [strom_eigenversorgung, strom_import]
    }, index=["Eigenerzeugung aus EE", "Stromimport"])

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename = region.get_results_path(filename=f"{key}_pie_import.png")

    plot_pie(labels=df_summary.index.tolist(),
             values=df_summary["var_value"].tolist(),
             title=f"Eigenerzeugung/Stromimporte {region_label}",
             filename=filename)


def generation_heat_high(region):
    df_dispatch_heat_high = region.scalars[region.scalars.var_name == "flow_out_heat_high"]
    df_dispatch_heat_high = df_dispatch_heat_high[df_dispatch_heat_high.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_heat_high_bar.png")
    filename = region.get_results_path(filename=f"{key}_heat_high_pie.png")

    barplot_e(df_dispatch_heat_high,
              unit="MWh_th",
              title=f"Wärmeversorgung (hoch) pro Technologie: {region_label}",
              filename=filename1)

    plot_pie_2(labels=df_dispatch_heat_high.name.tolist(),
               values=df_dispatch_heat_high.var_value.tolist(),
               unit="MWh_th",
               title=f"Anteil an Wärmeversorgung (hoch) pro Technologie: {region_label}",
               filename=filename)


def generation_heat_low_central(region):
    df_dispatch = region.scalars[region.scalars.var_name == "flow_out_heat_low_central"]
    df_dispatch = df_dispatch[df_dispatch.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_heat_low_central_bar.png")
    filename = region.get_results_path(filename=f"{key}_heat_low_central_pie.png")

    barplot_e(df_dispatch,
              unit="MWh_th",
              title=f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label}",
              filename=filename1)

    plot_pie_2(labels=df_dispatch.name.tolist(),
               values=df_dispatch.var_value.tolist(),
               unit="MWh_th",
               title=f"Anteil an Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label}",
               filename=filename)


def generation_heat_low_decentral(region):
    df_dispatch = region.scalars[region.scalars.var_name == "flow_out_heat_low_decentral"]
    df_dispatch = df_dispatch[df_dispatch.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_heat_low_decentral_bar.png")
    filename = region.get_results_path(filename=f"{key}_heat_low_decentral_pie.png")

    barplot_e(df_dispatch,
              unit="MWh_th",
              title=f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label}",
              filename=filename1)

    plot_pie_2(labels=df_dispatch.name.tolist(),
               values=df_dispatch.var_value.tolist(),
               unit="MWh_th",
               title=f"Anteil an Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label}",
               filename=filename)
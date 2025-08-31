from plots import(
    barplot_c,
    barplot_e,
    plot_pie,
    plot_pie_2,
)
import os
import pandas as pd

def capacities_opt_old(region):
    df_cap_opt = region.scalars[region.scalars["var_name"].str.startswith("invest_out")]
    #df_cap_opt = df_cap_opt[df_cap_opt["var_value"] != 0]

    return df_cap_opt

def capacities_opt(region):
    df_all = region.scalars[region.scalars["var_name"].str.startswith("invest_out")].copy()
    df_cap = df_all
    # filter only components with capacity != 0
    if not region.all_caps:
        df_cap = df_all[df_all["var_value"] != 0]

    # for heat storage (central & decentral) take var_name = invest
    df_hs =  region.scalars[region.scalars["var_name"] == "invest"].copy()
    hs_list = ["Wärmespeicher (niedrig, zentral)","Wärmespeicher (niedrig, dezentral)"]
    df_hs = df_hs[df_hs["name"].isin(hs_list)]

    # overwrite heatstore techs in df_cap
    df_cap = df_cap[~df_cap["name"].isin(hs_list)]
    df_cap = pd.concat([df_cap, df_hs], ignore_index=True)

    # Spezifisch prüfen: fehlt Solarkollektor (dezentral)?
    if "Solarkollektor (dezentral)" not in df_cap["name"].values:
        df_solar = df_all[df_all["name"] == "Solarkollektor (dezentral)"]
        if not df_solar.empty:
            df_cap = pd.concat([df_cap, df_solar], ignore_index=True)

    return df_cap


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


def cap_opt_bar_old(region):
    df_cap_opt = capacities_opt(region)

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename = region.get_results_path(filename=f"{key}_capacities_opt.png")

    barplot_c(df_cap_opt,
              title=f"Optimierte Kapazitäten {region_label}",
              filename=filename)

def cap_opt_bar(region, df_potentials=None, all_regions=False, single_region=False):
    df_cap_opt = capacities_opt(region)

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    df_cap_opt = df_cap_opt.copy()

    if df_potentials is not None:
        if "region" in df_potentials.columns:
            pot = df_potentials[df_potentials["region"] == key]
        else:
            pot = df_potentials  # aggregierte Variante
        df_cap_opt = pd.merge(
            df_cap_opt,
            pot[["tech", "capacity_potential"]],
            left_on="name",
            right_on="tech",
            how="left"
        )

    # plot settings
    filename = region.get_results_path(filename=f"{key}_capacities_opt.svg")
    if all_regions and single_region:
        title = f"Optimierte Kapazitäten {region_label} im Gemeindeverbund"
    elif not all_regions and single_region:
        title = f"Optimierte Kapazitäten {region_label} als Einzelregion"
    else:
        title = f"Optimierte Kapazitäten {region_label}"

    barplot_c(df_cap_opt,
              title=title,
              filename=filename,
              potential_data=df_cap_opt[["name", "capacity_potential"]] if "capacity_potential" in df_cap_opt else None)



def dispatch_bar(region, all_regions=False, single_region=False):
    df_dispatch_elec = dispatch_elec(region)
    df_dispatch_elec.var_value *= 1e-3

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    # plot settings
    filename1 = region.get_results_path(filename=f"{key}_dispatch_elec_bar.svg")
    filename = region.get_results_path(filename=f"{key}_dispatch_elec_pie.svg")

    if all_regions & single_region:
        title1 = f"Stromversorgung je Technologie {region_label} im Gemeindeverbund"
        title2 = f"Stromversorgung je Technologie {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Stromversorgung je Technologie {region_label} als Einzelregion"
        title2 = f"Stromversorgung je Technologie {region_label} als Einzelregion"
    else:
        title1 = f"Stromversorgung je Technologie {region_label}"
        title2 = f"Stromversorgung je Technologie {region_label}"


    barplot_e(df_dispatch_elec,
              unit="GWh",
              title=title1,
              filename=filename1)

    plot_pie_2(labels=df_dispatch_elec.name.tolist(),
               values=df_dispatch_elec.var_value.tolist(),
               title=title2,
               filename=filename)


def import_pie(region, all_regions=False, single_region=False):
    df_dispatch_elec = dispatch_elec(region)
    # df Eigenerzeugung
    df_gen_elec = df_dispatch_elec[~df_dispatch_elec["name"].str.contains("Stromimport|Batteriespeicher", case=False)]
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

    # plot settings
    filename = region.get_results_path(filename=f"{key}_pie_import.svg")

    if all_regions & single_region:
        title = f"Eigenerzeugung/Stromimporte {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title = f"Eigenerzeugung/Stromimporte {region_label} als Einzelregion"
    else:
        title = f"Eigenerzeugung/Stromimporte {region_label}"

    plot_pie(labels=df_summary.index.tolist(),
             values=df_summary["var_value"].tolist(),
             title=title,
             filename=filename)


def generation_heat_high(region, all_regions=False, single_region=False):
    df_dispatch_heat_high = region.scalars[region.scalars.var_name == "flow_out_heat_high"]
    df_dispatch_heat_high = df_dispatch_heat_high[df_dispatch_heat_high.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    # plot settings

    filename1 = region.get_results_path(filename=f"{key}_heat_high_bar.svg")
    filename = region.get_results_path(filename=f"{key}_heat_high_pie.svg")

    if all_regions & single_region:
        title1 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} im Gemeindeverbund"
        title2 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} als Einzelregion"
        title2 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} als Einzelregion"
    else:
        title1 = f"Wärmeversorgung (hoch) pro Technologie: {region_label}"
        title2 = f"Wärmeversorgung (hoch) pro Technologie: {region_label}"

    barplot_e(df_dispatch_heat_high,
              unit="MWh_th",
              title=title1,
              filename=filename1)

    plot_pie_2(labels=df_dispatch_heat_high.name.tolist(),
               values=df_dispatch_heat_high.var_value.tolist(),
               unit="MWh_th",
               title=title2,
               filename=filename)


def generation_heat_low_central(region, all_regions=False, single_region=False):
    df_dispatch = region.scalars[region.scalars.var_name == "flow_out_heat_low_central"]
    df_dispatch = df_dispatch[df_dispatch.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    # plot settings

    filename1 = region.get_results_path(filename=f"{key}_heat_low_central_bar.svg")
    filename = region.get_results_path(filename=f"{key}_heat_low_central_pie.svg")

    if all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} im Gemeindeverbund"
        title2 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} als Einzelregion"
        title2 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} als Einzelregion"
    else:
        title1 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label}"
        title2 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label}"

    barplot_e(df_dispatch,
              unit="MWh_th",
              title=title1,
              filename=filename1)

    plot_pie_2(labels=df_dispatch.name.tolist(),
               values=df_dispatch.var_value.tolist(),
               unit="MWh_th",
               title=title2,
               filename=filename)


def generation_heat_low_decentral(region, all_regions=False, single_region=False):
    df_dispatch = region.scalars[region.scalars.var_name == "flow_out_heat_low_decentral"]
    df_dispatch = df_dispatch[df_dispatch.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    # plot settings

    filename1 = region.get_results_path(filename=f"{key}_heat_low_decentral_bar.svg")
    filename = region.get_results_path(filename=f"{key}_heat_low_decentral_pie.svg")

    if all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} im Gemeindeverbund"
        title2 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} als Einzelregion"
        title2 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} als Einzelregion"
    else:
        title1 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label}"
        title2 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label}"

    barplot_e(df_dispatch,
              unit="MWh_th",
              title=title1,
              filename=filename1)

    plot_pie_2(labels=df_dispatch.name.tolist(),
               values=df_dispatch.var_value.tolist(),
               unit="MWh_th",
               title=title2,
               filename=filename)

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

def collect_capacity_potentials(base_path):
    """
    Liest alle relevanten CSV-Dateien mit Erneuerbaren-Potenzialen ein,
    extrahiert 'region', 'tech', 'capacity_potential' und wandelt 'tech' per Mapping
    in gelabelte Technologiebezeichnungen um.
    """
    import yaml

    def load_label_mapping(yaml_path="de.yml"):
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def apply_label_mapping(df, mapping, column="name"):
        df[column] = df[column].map(mapping).fillna(df[column])
        return df

    technologies = [
        "electricity-pv_agri_horizontal",
        "electricity-pv_agri_vertical",
        "electricity-pv_ground",
        "electricity-pv_rooftop",
        "electricity-wind",
        "heat_low_decentral-solarthermal_plant"
    ]

    df_list = []

    mapping = load_label_mapping("de.yml")

    for tech in technologies:
        file_path = os.path.join(base_path, f"{tech}.csv")
        if not os.path.exists(file_path):
            print(f"WARNUNG: Datei nicht gefunden: {file_path}")
            continue

        df = read_csv_auto_sep(file_path)
        df[["region", "tech"]] = df["name"].str.split("-", n=1, expand=True)
        df = df.loc[:, ["region", "tech", "capacity_potential"]]
        df = apply_label_mapping(df, mapping, column="tech")  # 🆕 Mapping anwenden
        df_list.append(df)

    if not df_list:
        raise ValueError("Keine Potenzialdaten gefunden. Bitte Dateipfade prüfen.")

    df_all = pd.concat(df_list, ignore_index=True)
    return df_all


def collect_renewable_potentials(base_path="input_data/01_ALL_REGIONS/2045_scenario/preprocessed/data/elements"):
    """
    Creates two files:
    1. results/potentials.csv: Potentials per region and technology
    2. results/potentials_overall.csv: Total potential per technology
    """
    # make sure results folder exists
    os.makedirs("results", exist_ok=True)

    df_potentials_regions = collect_capacity_potentials(base_path)

    # save all potentials per region
    df_potentials_regions.to_csv("results/potentials.csv", index=False)
    print("✅ Potentials per region saved at: results/potentials.csv")

    # aggregate by technology
    df_potentials_overall = (
        df_potentials_regions
        .groupby("tech", as_index=False)["capacity_potential"]
        .sum()
    )

    df_potentials_overall.to_csv("results/potentials_overall.csv", index=False)
    print("✅ Total potentials saved at: results/potentials_overall.csv")

    return df_potentials_regions, df_potentials_overall
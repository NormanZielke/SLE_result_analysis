import os
import pandas as pd
import yaml

from plots import (
    barplot_c,
    barplot_e,
    plot_pie,
    plot_pie_2,
)

from helpers import (
    read_csv_auto_sep
)


def capacities_opt(region):
    """
    Build the capacity table used for capacity plots.

    The function collects capacity investments (``var_name`` starts with
    ``"invest_out"``). If ``region.all_caps`` is ``False``, rows with
    zero capacities are filtered out. Heat storages are handled as a
    special case by pulling ``var_name == "invest"`` for
    ``["Wärmespeicher (niedrig, zentral)", "Wärmespeicher (niedrig, dezentral)"]``.
    Additionally, the decentralized solar collector entry is ensured to
    be present if available in the raw list.

    Parameters
    ----------
    region : object
        Region-like object with attributes
        - ``all_caps`` : bool
        - ``scalars`` : pandas.DataFrame with ``name``, ``var_name``, ``var_value``.

    Returns
    -------
    pandas.DataFrame
        Capacity table ready for plotting with at least columns
        ``name`` and ``var_value``.
    """

    df_all = region.scalars[region.scalars["var_name"].str.startswith("invest_out")].copy()
    df_cap = df_all

    # Optionally filter components with capacity == 0
    if not region.all_caps:
        df_cap = df_all[df_all["var_value"] != 0]

    # Heat storages: use 'invest' instead of 'invest_out'
    df_hs = region.scalars[region.scalars["var_name"] == "invest"].copy()
    hs_list = ["Wärmespeicher (niedrig, zentral)", "Wärmespeicher (niedrig, dezentral)"]
    df_hs = df_hs[df_hs["name"].isin(hs_list)]

    # Overwrite heat storage entries from df_cap with df_hs versions
    df_cap = df_cap[~df_cap["name"].isin(hs_list)]
    df_cap = pd.concat([df_cap, df_hs], ignore_index=True)

    # Ensure decentralized solar collector is kept if present upstream
    if "Solarkollektor (dezentral)" not in df_cap["name"].values:
        df_solar = df_all[df_all["name"] == "Solarkollektor (dezentral)"]
        if not df_solar.empty:
            df_cap = pd.concat([df_cap, df_solar], ignore_index=True)

    return df_cap


def dispatch_elec(region):
    """
    Select non-zero electricity dispatch rows.

    Parameters
    ----------
    region : object
        Region-like object exposing a pandas DataFrame ``scalars``.

    Returns
    -------
    pandas.DataFrame
        Subset where ``var_name == "flow_out_electricity"`` and
        ``var_value != 0``.
    """

    df_dispatch_elec = region.scalars[region.scalars.var_name == "flow_out_electricity"]
    df_dispatch_elec = df_dispatch_elec[df_dispatch_elec.var_value != 0]
    return df_dispatch_elec


def techs_none(region):
    """
    Write out the list of unused technologies (capacity == 0).

    A CSV is written to the region-specific results folder with one column
    named ``f"techs_none_{region_id}"`` and one row per unused technology.

    Parameters
    ----------
    region : object
        Must provide:
        - ``region_id`` : str
        - ``scalars`` : pandas.DataFrame
        - ``get_results_path(filename)`` : callable

    Returns
    -------
    None
        Writes a CSV file to disk as a side effect.
    """
    df_capacities = region.scalars[region.scalars["var_name"].str.startswith("invest_out")]
    df_cap_none = df_capacities[df_capacities["var_value"] == 0]
    techs_none = df_cap_none.name.unique()

    region_id = region.region_id
    df_none = pd.DataFrame(techs_none, columns=[f"techs_none_{region_id}"])

    output_path = region.get_results_path(filename=f"{region_id}_nicht_verwendete_technologien.csv")
    df_none.to_csv(output_path, index=True)


def cap_opt_bar(region, df_potentials=None, all_regions=False, single_region=False):
    """
    Plot optimized capacities with optional potential overlay.

    If ``df_potentials`` is provided, the function merges corresponding
    potential values (column ``capacity_potential``) by technology name
    and shows them as markers on top of the bars.

    Parameters
    ----------
    region : object
        Region-like object providing ``scalars``, ``region_id``,
        ``get_results_path``.
    df_potentials : pandas.DataFrame or None, optional
        Either a per-region table with columns
        ``["region", "tech", "capacity_potential"]`` or an aggregated table
        with columns ``["tech", "capacity_potential"]``. If provided,
        potentials are aligned to bar names via a left-join.
    all_regions : bool, optional
        If ``True`` and ``single_region`` is also ``True``, titles indicate
        the combined-solution context, by default ``False``.
    single_region : bool, optional
        If ``True``, titles indicate a single-region context (either alone
        or in the combined-solution view), by default ``False``.

    Returns
    -------
    None
        Saves an ``.svg`` plot to the region's results folder.
    """
    df_cap_opt = capacities_opt(region)

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    df_cap_opt = df_cap_opt.copy()

    # Attach potential data if available
    if df_potentials is not None:
        if "region" in df_potentials.columns:
            pot = df_potentials[df_potentials["region"] == key]
        else:
            pot = df_potentials  # aggregated variant
        df_cap_opt = pd.merge(
            df_cap_opt,
            pot[["tech", "capacity_potential"]],
            left_on="name",
            right_on="tech",
            how="left",
        )

    # Configure title and output path
    filename = region.get_results_path(filename=f"{key}_capacities_opt.svg")
    if all_regions and single_region:
        title = f"Optimierte Kapazitäten {region_label} im Gemeindeverbund"
    elif not all_regions and single_region:
        title = f"Optimierte Kapazitäten {region_label} als Einzelregion"
    else:
        title = f"Optimierte Kapazitäten {region_label}"

    barplot_c(
        df_cap_opt,
        title=title,
        filename=filename,
        potential_data=df_cap_opt[["name", "capacity_potential"]] if "capacity_potential" in df_cap_opt else None,
    )


def dispatch_bar(region, all_regions=False, single_region=False):
    """
    Plot electricity supply by technology as bar chart and pie chart.

    The function builds the electricity dispatch for the region, converts
    MWh to GWh (for plotting), and saves both a bar chart and a pie chart.

    Parameters
    ----------
    region : object
        Region-like object
    all_regions : bool, optional
        Title context for combined solution, by default ``False``.
    single_region : bool, optional
        Title context for single region, by default ``False``.

    Returns
    -------
    None
        Saves ``*_dispatch_elec_bar.svg`` and ``*_dispatch_elec_pie.svg``.
    """

    df_dispatch_elec = dispatch_elec(region)
    df_dispatch_elec.var_value *= 1e-3  # convert MWh → GWh for plotting

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_dispatch_elec_bar.svg")
    filename = region.get_results_path(filename=f"{key}_dispatch_elec_pie.svg")

    if all_regions & single_region:
        title1 = f"Stromversorgung je Technologie {region_label} im Gemeindeverbund"
        title2 = f"Stromversorgung je Technologie {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Stromversorgung je Technologie {region_label} als Einzelregion"
        title2 = f"Stromversorgung je Technologie {region_label} als Einzelregion"
    else: # if both false, title for aggregated solution
        title1 = f"Stromversorgung je Technologie {region_label}"
        title2 = f"Stromversorgung je Technologie {region_label}"

    barplot_e(
        df=df_dispatch_elec,
        unit="GWh",
        title=title1,
        filename=filename1,
    )

    plot_pie_2(
        labels=df_dispatch_elec.name.tolist(),
        values=df_dispatch_elec.var_value.tolist(),
        title=title2,
        filename=filename,
    )


def import_pie(region, all_regions=False, single_region=False):
    """
    Plot a two-slice pie chart: self-supply vs. electricity import.

    Batteries are excluded from self-supply. Values are plotted in GWh.

    Parameters
    ----------
    region : object
        Region-like object
    all_regions : bool, optional
        Title context for combined solution, by default ``False``.
    single_region : bool, optional
        Title context for single region, by default ``False``.

    Returns
    -------
    None
        Saves a ``*_pie_import.svg`` pie chart.
    """

    df_dispatch_elec = dispatch_elec(region)

    # Self-generation excludes 'Stromimport' and batteries
    df_gen_elec = df_dispatch_elec[
        ~df_dispatch_elec["name"].str.contains("Stromimport|Batteriespeicher", case=False)
    ]

    strom_eigenversorgung = df_gen_elec.var_value.sum() * 1e-3  # MWh → GWh
    strom_import = df_dispatch_elec[df_dispatch_elec["name"] == "Stromimport"].var_value.sum() * 1e-3

    df_summary = pd.DataFrame({"var_value": [strom_eigenversorgung, strom_import]},
                              index=["Eigenerzeugung aus EE", "Stromimport"])

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename = region.get_results_path(filename=f"{key}_pie_import.svg")

    if all_regions & single_region:
        title = f"Eigenerzeugung/Stromimporte {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title = f"Eigenerzeugung/Stromimporte {region_label} als Einzelregion"
    else: # if both false, title for aggregated solution
        title = f"Eigenerzeugung/Stromimporte {region_label}"

    plot_pie(
        labels=df_summary.index.tolist(),
        values=df_summary["var_value"].tolist(),
        title=title,
        filename=filename,
    )


def generation_heat_high(region, all_regions=False, single_region=False):
    """
    Plot high-temperature heat generation by technology.

    Produces a bar chart and a pie chart (values in ``MWh_th``).

    Parameters
    ----------
    region : object
        Region-like object exposing ``scalars``.
    all_regions : bool, optional
        Title context for combined solution, by default ``False``.
    single_region : bool, optional
        Title context for single region, by default ``False``.

    Returns
    -------
    None
        Saves ``*_heat_high_bar.svg`` and ``*_heat_high_pie.svg``.
    """
    df_dispatch_heat_high = region.scalars[region.scalars.var_name == "flow_out_heat_high"]
    df_dispatch_heat_high = df_dispatch_heat_high[df_dispatch_heat_high.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_heat_high_bar.svg")
    filename = region.get_results_path(filename=f"{key}_heat_high_pie.svg")

    if all_regions & single_region:
        title1 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} im Gemeindeverbund"
        title2 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} als Einzelregion"
        title2 = f"Wärmeversorgung (hoch) pro Technologie: {region_label} als Einzelregion"
    else: # # if both false, title for aggregated solution
        title1 = f"Wärmeversorgung (hoch) pro Technologie: {region_label}"
        title2 = f"Wärmeversorgung (hoch) pro Technologie: {region_label}"

    barplot_e(
        df=df_dispatch_heat_high,
        unit="MWh_th",
        title=title1,
        filename=filename1,
    )

    plot_pie_2(
        labels=df_dispatch_heat_high.name.tolist(),
        values=df_dispatch_heat_high.var_value.tolist(),
        unit="MWh_th",
        title=title2,
        filename=filename,
    )


def generation_heat_low_central(region, all_regions=False, single_region=False):
    """
    Plot low-temperature **central** heat generation by technology.

    Produces a bar chart and a pie chart (values in ``MWh_th``).

    Parameters
    ----------
    region : object
        Region-like object exposing ``scalars``.
    all_regions : bool, optional
        Title context for combined solution, by default ``False``.
    single_region : bool, optional
        Title context for single region, by default ``False``.

    Returns
    -------
    None
        Saves ``*_heat_low_central_bar.svg`` and ``*_heat_low_central_pie.svg``.
    """

    df_dispatch = region.scalars[region.scalars.var_name == "flow_out_heat_low_central"]
    df_dispatch = df_dispatch[df_dispatch.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_heat_low_central_bar.svg")
    filename = region.get_results_path(filename=f"{key}_heat_low_central_pie.svg")

    if all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} im Gemeindeverbund"
        title2 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} als Einzelregion"
        title2 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label} als Einzelregion"
    else: # if both false, title for aggregated solution
        title1 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label}"
        title2 = f"Wärmeversorgung (niedrig, zentral) pro Technologie: {region_label}"

    barplot_e(
        df=df_dispatch,
        unit="MWh_th",
        title=title1,
        filename=filename1,
    )

    plot_pie_2(
        labels=df_dispatch.name.tolist(),
        values=df_dispatch.var_value.tolist(),
        unit="MWh_th",
        title=title2,
        filename=filename,
    )


def generation_heat_low_decentral(region, all_regions=False, single_region=False):
    """
    Plot low-temperature **decentral** heat generation by technology.

    Produces a bar chart and a pie chart (values in ``MWh_th``).

    Parameters
    ----------
    region : object
        Region-like object exposing ``scalars`` and accessors.
    all_regions : bool, optional
        Title context for combined solution, by default ``False``.
    single_region : bool, optional
        Title context for single region, by default ``False``.

    Returns
    -------
    None
        Saves ``*_heat_low_decentral_bar.svg`` and ``*_heat_low_decentral_pie.svg``.
    """

    df_dispatch = region.scalars[region.scalars.var_name == "flow_out_heat_low_decentral"]
    df_dispatch = df_dispatch[df_dispatch.var_value != 0]

    key = region.region_id
    default_label = key
    name_map = getattr(region, "region_name_map", {})
    region_label = name_map.get(key, default_label)

    filename1 = region.get_results_path(filename=f"{key}_heat_low_decentral_bar.svg")
    filename = region.get_results_path(filename=f"{key}_heat_low_decentral_pie.svg")

    if all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} im Gemeindeverbund"
        title2 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} im Gemeindeverbund"
    elif not all_regions & single_region:
        title1 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} als Einzelregion"
        title2 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label} als Einzelregion"
    else: # # if both false, title for aggregated solution
        title1 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label}"
        title2 = f"Wärmeversorgung (niedrig, dezentral) pro Technologie: {region_label}"

    barplot_e(
        df=df_dispatch,
        unit="MWh_th",
        title=title1,
        filename=filename1,
    )

    plot_pie_2(
        labels=df_dispatch.name.tolist(),
        values=df_dispatch.var_value.tolist(),
        unit="MWh_th",
        title=title2,
        filename=filename,
    )


def collect_capacity_potentials(base_path):
    """
    Collect renewable energy capacity potentials from CSV files.

    This function reads multiple CSV files containing renewable
    potentials, extracts the columns ``region``, ``tech``, and
    ``capacity_potential``, and applies a label mapping to transform
    technology codes into human-readable names.

    Parameters
    ----------
    base_path : str
        Path to the folder containing the CSV files.

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns:

        - ``region`` : str
            Region identifier.
        - ``tech`` : str
            Technology label (after mapping).
        - ``capacity_potential`` : float
            Installed capacity potential in MW.

    Raises
    ------
    ValueError
        If no potential data files are found in the given path.
    """
    def load_label_mapping(yaml_path="de.yml"):
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def apply_label_mapping(df, mapping, column="name"):
        df[column] = df[column].map(mapping).fillna(df[column])
        return df

    # List of technologies to read
    technologies = [
        "electricity-pv_agri_horizontal",
        "electricity-pv_agri_vertical",
        "electricity-pv_ground",
        "electricity-pv_rooftop",
        "electricity-wind",
        "heat_low_decentral-solarthermal_plant",
    ]

    df_list = []
    mapping = load_label_mapping("de.yml")

    for tech in technologies:
        file_path = os.path.join(base_path, f"{tech}.csv")
        if not os.path.exists(file_path):
            print(f"⚠️ WARNING: File not found: {file_path}")
            continue

        df = read_csv_auto_sep(file_path)
        # Split 'name' into region and technology parts
        df[["region", "tech"]] = df["name"].str.split("-", n=1, expand=True)
        df = df.loc[:, ["region", "tech", "capacity_potential"]]
        # Apply mapping to technology names
        df = apply_label_mapping(df, mapping, column="tech")
        df_list.append(df)

    if not df_list:
        raise ValueError("No potential data found. Please check the file paths.")

    df_all = pd.concat(df_list, ignore_index=True)
    return df_all


def collect_renewable_potentials(
        base_path="input_data/01_ALL_REGIONS/2045_scenario/preprocessed/data/elements",
        results_path="results",
):
    """
    Collect and aggregate renewable capacity potentials.

    This function loads regional renewable energy potentials from CSV files,
    stores them in two output files, and returns the results as DataFrames.

    Outputs
    -------
    - ``results/potentials.csv`` : potentials per region and technology.
    - ``results/potentials_overall.csv`` : aggregated total potentials per technology.

    Parameters
    ----------
    base_path : str
        Path to the folder containing the input CSV files.
        Default is ``"input_data/01_ALL_REGIONS/2045_scenario/preprocessed/data/elements"``.

    results_path: str
        Path to the folder containing the results CSV files.
        Default is "results"

    Returns
    -------
    tuple of pandas.DataFrame
        - ``df_potentials_regions`` : DataFrame with columns
          ``[region, tech, capacity_potential]``.
        - ``df_potentials_overall`` : DataFrame with columns
          ``[tech, capacity_potential]`` (aggregated sum across regions).
    """
    # Ensure output directory exists
    os.makedirs(results_path, exist_ok=True)

    # Load potentials per region + technology
    df_potentials_regions = collect_capacity_potentials(base_path)

    # Save per-region potentials
    df_potentials_regions.to_csv(f"{results_path}/potentials.csv", index=False)
    print("✅ Potentials per region saved at: results/potentials.csv")

    # Aggregate over regions by technology
    df_potentials_overall = (
        df_potentials_regions.groupby("tech", as_index=False)["capacity_potential"].sum()
    )

    df_potentials_overall.to_csv(f"{results_path}/potentials_overall.csv", index=False)
    print("✅ Total potentials saved at: results/potentials_overall.csv")

    return df_potentials_regions, df_potentials_overall

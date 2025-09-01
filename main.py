"""
Main orchestration script for regional and aggregated post-processing.

This module:
1) Collects renewable capacity potentials from preprocessed CSVs and stores
   two helper files under ``results/``.
2) Computes and plots results for each single region (standalone and within
   the combined ALL_REGIONS solution).
3) Computes aggregated views for:
   - the combined ALL_REGIONS solution, and
   - the sum of all Single_Regions.
"""

from class_region import region
from class_aggregated_region import aggregated_region
from calc_results import (
    collect_renewable_potentials,
)
from helpers import (
    read_csv_auto_sep
)

# Configuration

args = {
    "region_id_dict": {
        "r120640428428": "Rüdersdorf",
        "r120640472472": "Strausberg",
        "r120670124124": "Erkner",
        "r120670201201": "Grünheide",
    },
    # Directory with CSVs that contain renewable capacity potentials
    "renewables_pot_csv_directory": "input_data/01_ALL_REGIONS/2045_scenario/preprocessed/data/elements",
    "all_capacities": True, # If True, keep technologies with zero capacity in capacity plots
    "results_dir": "results_2", # central folder/directory for all output paths
}


def calculate_single_regions(args, region_id, all_regions=False, single_region=True):
    """
    Compute and plot results for a single region.

    Depending on ``all_regions``, the function either reads the region's
    own ``scalars.csv`` or filters the combined ALL_REGIONS file for the
    given ``region_id``. It then produces capacity, dispatch, import pie,
    and heat generation plots, and writes a CSV of unused technologies.

    Parameters
    ----------
    args : dict
        Configuration dictionary containing at least:
        - ``"region_id_dict"`` : mapping from region ids to display names,
        - ``"all_capacities"`` : bool, whether to keep zero capacities.
    region_id : str
        Region identifier (e.g., ``"r120640472472"``).
    all_regions : bool, optional
        If ``True``, use the combined ALL_REGIONS scalars file and filter
        rows for this region, by default ``False``.
        If ``False``, use the single solution for this region, by default
    single_region : bool, optional
        Title context to indicate single-region view in plots, by default ``True``.

    Returns
    -------
    None
        Side effects: figures and CSVs are written under ``results/...``.
    """
    # Select path to scalars depending on context
    if all_regions:
        region_folder = "input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv"
    else:
        region_folder = f"input_data/Single_Regions/{region_id}/2045_scenario/postprocessed/scalars.csv"

    # Build region container; `from_combined_file` controls filtering/stripping behavior
    region_1 = region(args, csv_folder=region_folder, region_id=region_id, from_combined_file=all_regions)

    # Optional human-readable names for titles/labels
    region_1.region_name_map = args.get("region_id_dict", {})

    # Plot capacities (with potential overlay), list unused techs, and plot summed energydispatch (electricity/heat)
    region_1.cap_opt_bar(df_potentials=df_potentials_region, all_regions=all_regions, single_region=single_region)
    region_1.techs_none()
    region_1.dispatch_bar(all_regions=all_regions, single_region=single_region)
    region_1.import_pie(all_regions=all_regions, single_region=single_region)
    region_1.generation_heat_high(all_regions=all_regions, single_region=single_region)
    region_1.generation_heat_low_central(all_regions=all_regions, single_region=single_region)
    region_1.generation_heat_low_decentral(all_regions=all_regions, single_region=single_region)


def calculate_aggregated_results():
    """
    Compute and plot aggregated results for ALL_REGIONS and for concatenated Single_Regions.

    This function creates two ``aggregated_region`` containers:
    1) A container over the combined ALL_REGIONS solution.
    2) A container over a list of Single_Regions scalars files (aggregated).

    For each container, capacity, dispatch, import pie, and heat plots are produced.

    Returns
    -------
    None
        Side effects: figures are written under:
        - ``results/01_ALL_REGIONS_aggregated/``
        - ``results/Single_Region_aggregated/``
    """

    out_base = args["results_dir"]

    # Aggregation over ALL_REGIONS (single combined file)
    agg_all = aggregated_region(
        args,
        region_id="Gemeindeverbund",
        csv_paths="input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv",
        output_folder=f"{out_base}/01_ALL_REGIONS_aggregated/",
    )

    agg_all.cap_opt_bar(df_potentials=df_potentials_overall)
    agg_all.techs_none()
    agg_all.dispatch_bar()
    agg_all.import_pie()
    agg_all.generation_heat_high()
    agg_all.generation_heat_low_central()
    agg_all.generation_heat_low_decentral()

    # Aggregation over all Single_Regions (concatenate multiple files)
    csv_paths = [
        f"input_data/Single_Regions/{r}/2045_scenario/postprocessed/scalars.csv"
        for r in args["region_id_dict"]
    ]

    agg_single = aggregated_region(
        args,
        region_id="Einzelregionen",
        csv_paths=csv_paths,
        output_folder=f"{out_base}/Single_Region_aggregated/",
    )

    agg_single.cap_opt_bar(df_potentials=df_potentials_overall)
    agg_single.techs_none()
    agg_single.dispatch_bar()
    agg_single.import_pie()
    agg_single.generation_heat_high()
    agg_single.generation_heat_low_central()
    agg_single.generation_heat_low_decentral()


if __name__ == "__main__":

    # Collect renewable potentials and create helper CSVs
    collect_renewable_potentials(
        base_path=args["renewables_pot_csv_directory"],
        results_path=args["results_dir"],
    )

    # Load the generated potentials for later overlay/aggregation
    df_potentials_region = read_csv_auto_sep("results/potentials.csv")
    df_potentials_overall = read_csv_auto_sep("results/potentials_overall.csv")

    # Compute regional results
    #   a) Single-region runs (per region)
    #   b) Region filtered from the combined ALL_REGIONS file

    for region_id in args["region_id_dict"]:
        # (a) Standalone single-region results
        calculate_single_regions(args, region_id, all_regions=False, single_region=True)

    for region_id in args["region_id_dict"]:
        # (b) Same region viewed within the combined ALL_REGIONS file
        calculate_single_regions(args, region_id, all_regions=True, single_region=True)

    # Aggregated views
    calculate_aggregated_results()

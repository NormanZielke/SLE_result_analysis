
from class_region import region
from class_aggregated_region import aggregated_region
from calc_results import (
    collect_renewable_potentials,
    read_csv_auto_sep)


args = {
    "region_id_dict":{
        "r120640428428": "Rüdersdorf",
        "r120640472472": "Strausberg",
        "r120670124124": "Erkner",
        "r120670201201": "Grünheide",
    },
    "csv_paths":{
        "aggregated_ALL_REGION_solution": "input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv",
        "aggregated_ALL_REGION_solution_permutation": "input_data/01_ALL_REGIONS/2045_scenario/robust_results/cost/26/2045_scenario/postprocessed"
    },
    "all_capacities": False, # activate all considered Technologies in Capacity-plot
}

def calculate_single_regions(args, region_id, all_regions=False, single_region=True):

    if all_regions:
        region_folder = f'input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv'
    else:
        region_folder = f'input_data/Single_Regions/{region_id}/2045_scenario/postprocessed/scalars.csv'

    region_1 = region(args, csv_folder = region_folder, region_id = region_id, from_combined_file= all_regions)

    region_1.region_name_map = args.get("region_id_dict", {})

    region_1.cap_opt_bar(df_potentials=df_potentials_region, all_regions=all_regions, single_region=single_region)
    region_1.techs_none()
    region_1.dispatch_bar(all_regions=all_regions, single_region=single_region)
    region_1.import_pie(all_regions=all_regions, single_region=single_region)
    region_1.generation_heat_high(all_regions=all_regions, single_region=single_region)
    region_1.generation_heat_low_central(all_regions=all_regions, single_region=single_region)
    region_1.generation_heat_low_decentral(all_regions=all_regions, single_region=single_region)

def calculate_aggregated_results():
    # 1. ALL_REGIONS aggregieren
    agg_all = aggregated_region(
        args,
        region_id="Gemeindeverbund",
        csv_paths="input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv",
        output_folder="results/01_ALL_REGIONS_aggregated/"
    )

    agg_all.cap_opt_bar(df_potentials=df_potentials_overall)
    agg_all.techs_none()
    agg_all.dispatch_bar()
    agg_all.import_pie()
    agg_all.generation_heat_high()
    agg_all.generation_heat_low_central()
    agg_all.generation_heat_low_decentral()

    # 2. Single_Regions zusammenführen
    csv_paths = [
        f"input_data/Single_Regions/{r}/2045_scenario/postprocessed/scalars.csv"
        for r in args["region_id_dict"]
    ]

    agg_single = aggregated_region(
        args,
        region_id="Einzelregionen",
        csv_paths=csv_paths,
        output_folder="results/Single_Region_aggregated/"
    )

    agg_single.cap_opt_bar(df_potentials=df_potentials_overall)
    agg_single.techs_none()
    agg_single.dispatch_bar()
    agg_single.import_pie()
    agg_single.generation_heat_high()
    agg_single.generation_heat_low_central()
    agg_single.generation_heat_low_decentral()



if __name__ == "__main__":
    # collect renewable potentials and create .csv for regions and overall
    collect_renewable_potentials(
        base_path="input_data/01_ALL_REGIONS/2045_scenario/preprocessed/data/elements")

    # ✅ Potenziale aus CSV einlesen
    df_potentials_region = read_csv_auto_sep("results/potentials.csv")
    df_potentials_overall = read_csv_auto_sep("results/potentials_overall.csv")

    # calcualte results from single-solutions
    for region_id in args["region_id_dict"]:
        calculate_single_regions(args, region_id, all_regions=False, single_region=True)

    # calcualte results from combined-solution
    for region_id in args["region_id_dict"]:
        calculate_single_regions(args, region_id, all_regions=True, single_region=True)

    # calculate aggregated results
    #calculate_aggregated_results()

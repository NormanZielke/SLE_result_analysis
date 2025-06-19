
from class_region import region
from class_aggregated_region import aggregated_region


args = {
    "region_id":[
        "r120640428428",
        "r120640472472",
        "r120670124124",
        "r120670201201",
    ]
}

def calculate_single_regions(args, region_id, all_regions=False):

    if all_regions:
        region_folder = f'input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv'
    else:
        region_folder = f'input_data/Single_Regions/{region_id}/2045_scenario/postprocessed/scalars.csv'

    region_1 = region(args, csv_folder = region_folder, region_id = region_id, from_combined_file= all_regions)
    region_1.cap_opt_bar()
    region_1.techs_none()
    region_1.dispatch_bar()
    region_1.import_pie()
    region_1.generation_pie_electricity()
    region_1.generation_heat_high()
    region_1.generation_heat_low_central()
    region_1.generation_heat_low_decentral()

def calculate_aggregated_results():
    # 1. ALL_REGIONS aggregieren
    agg_all = aggregated_region(
        region_id="ALL_REGIONS",
        csv_paths="input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv",
        output_folder="results/01_ALL_REGIONS_aggregated/"
    )

    agg_all.cap_opt_bar()
    agg_all.techs_none()
    agg_all.dispatch_bar()
    agg_all.import_pie()
    agg_all.generation_pie_electricity()
    agg_all.generation_heat_high()
    agg_all.generation_heat_low_central()
    agg_all.generation_heat_low_decentral()

    # 2. Single_Regions zusammenführen
    csv_paths = [
        f"input_data/Single_Regions/{r}/2045_scenario/postprocessed/scalars.csv"
        for r in args["region_id"]
    ]

    agg_single = aggregated_region(
        region_id="Single_Regions",
        csv_paths=csv_paths,
        output_folder="results/Single_Region_aggregated/"
    )

    agg_single.cap_opt_bar()
    agg_single.techs_none()
    agg_single.dispatch_bar()
    agg_single.import_pie()
    agg_single.generation_pie_electricity()
    agg_single.generation_heat_high()
    agg_single.generation_heat_low_central()
    agg_single.generation_heat_low_decentral()

if __name__ == "__main__":
    # calcualte results from single-solutions
    for region_id in args["region_id"]:
        calculate_single_regions(args, region_id, all_regions=False)

    # calcualte results from combined-solution
    for region_id in args["region_id"]:
        calculate_single_regions(args, region_id, all_regions=True)
    # calculate aggregated results
    calculate_aggregated_results()

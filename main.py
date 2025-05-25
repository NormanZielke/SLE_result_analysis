
from class_region import region



args = {
    "region_id":[
        "r120640428428",
        "r120640472472",
        "r120670124124",
        "r120670201201",
    ]
}

# === sinlge region ===

region_id = "r120670201201"

#region_folder = f'input_data/Single_Regions/{region_id}/2045_scenario/postprocessed/scalars.csv'

region_folder = f'input_data/01_ALL_REGIONS/2045_scenario/postprocessed/scalars.csv'

region_1 = region(args, csv_folder = region_folder, region_id = region_id, from_combined_file= True)

region_1.cap_opt_bar()

region_1.techs_none()

region_1.dispatch_bar()

region_1.import_pie()

region_1.generation_pie_electricity()

region_1.generation_heat_high()

region_1.generation_heat_low_central()

region_1.generation_heat_low_decentral()

# === all regions ===



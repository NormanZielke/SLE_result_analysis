
from class_region import region



args = {
    "region_id":[
        "r120640428428",
        "r120640472472",
        "r120670124124",
        "r120670201201",
    ]
}

region_id = "r120640428428"

region_folder = f'Single_Regions/{region_id}/2045_scenario/postprocessed/scalars.csv'

region_1 = region(args, csv_folder = region_folder, region_id = region_id)


region_1.cap_opt_bar()

region_1.techs_none()

region_1.dispatch_bar()

region_1.import_pie()

region_1.generation_pie_electricity()

region_1.generation_heat_high()
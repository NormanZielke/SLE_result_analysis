import pandas as pd
import numpy as np
from class_region import region
args = {
    "region":[
        "r120640428428",
        "r120640472472",
        "r120670124124",
        "r120670201201",
    ]
}

region_id = "r120640428428"

region_folder = f'Single_Regions/{region_id}/2045_scenario/postprocessed/scalars.csv'

region_1 = region(csv_folder = region_folder, region_id = region_id)

print(region_1.scalars)

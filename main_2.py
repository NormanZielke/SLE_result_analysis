from class_region import region

region_ids = [
    "r120640428428",
    "r120640472472",
    "r120670124124",
    "r120670201201",
]

regions = {}

for rid in region_ids:
    path = f"Single_Regions/{rid}/2045_scenario/postprocessed/scalars.csv"
    regions[rid] = region(csv_folder=path, region_id=rid)

# Beispiel: Zugriff auf die erste Region
first_region = regions[region_ids[0]]
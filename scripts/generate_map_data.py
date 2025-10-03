import pandas as pd
import geopandas as gpd
import json

csv_paths = [
    "./PenAmericaData/PEN America's Index of School Book Bans (July 1, 2022 - June 30, 2023) - Sorted by Author & Title.csv",
    "./PenAmericaData/Pen America's Index of School Books Bans 2024 2025.csv"
]
csv_data = pd.concat([pd.read_csv(path) for path in csv_paths], ignore_index=True)

geojson_path = "./geojson/School_District_Composites_SY_2023-24_TL_24.geojson"
geojson_data = gpd.read_file(geojson_path)
geojson_data["geometry"] = geojson_data["geometry"].simplify(tolerance=0.01, preserve_topology=True)

replacements = {
    "Horry County Schools": "Horry County School District",
    "Lake County Schools": "Lake County School District",
    "Wentzville School District": "Wentzville R-IV School District",
    "Kirkwood School District": "Kirkwood R-VII School District",
    "Sumner County Schools": "Sumner County School District",
    "Gale-Ettrick School District": "Galesville-Ettrick-Trempealeau School District",
    "North Kansas City Schools": "North Kansas City 74 School District",
    "Abington Public Schools": "Abington School District",
    "Sioux Valley School District": "Sioux Valley School District 05-5",
    "Natrona County Schools": "Natrona County School District 1"
}

csv_data["District"] = csv_data["District"].str.strip()

district_ban_counts = csv_data["District"].value_counts().to_dict()

geojson_data["ban_count"] = 0  

for index, row in geojson_data.iterrows():
    district_name = row["NAME"]  
    replacement_name = None  
    for csv_district, geojson_district in replacements.items():
        if geojson_district == district_name:
            replacement_name = csv_district
            break
    if replacement_name and replacement_name in district_ban_counts:
        geojson_data.at[index, "ban_count"] = district_ban_counts[replacement_name]
    elif district_name in district_ban_counts:
        geojson_data.at[index, "ban_count"] = district_ban_counts[district_name]

output_geojson_path = "./geojson/districts_with_ban_counts.geojson"
geojson_data.to_file(output_geojson_path, driver="GeoJSON")

print(f"GeoJSON with ban counts saved to {output_geojson_path}")
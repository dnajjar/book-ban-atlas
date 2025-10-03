import pandas as pd
import geopandas as gpd

# Load the CSV file
csv_path = "PEN America's Index of School Book Bans (July 1, 2022 - June 30, 2023) - Sorted by Author & Title.csv"
csv_data = pd.read_csv(csv_path)

# Extract unique districts from the CSV
csv_districts = set(csv_data["District"].dropna().unique())

# Load the GeoJSON file
geojson_path = "School_District_Composites_SY_2023-24_TL_24.geojson"
geojson_data = gpd.read_file(geojson_path)

# Extract unique districts from the GeoJSON
geojson_districts = set(geojson_data["NAME"].dropna().unique())  

# Find districts in the CSV that are not in the GeoJSON
missing_districts = csv_districts - geojson_districts

# Output the missing districts
print("Districts in the CSV but not in the GeoJSON:")
for district in missing_districts:
    print(district)

# Optionally, save the missing districts to a file
missing_districts_path = "missing_districts.csv"
pd.DataFrame({"Missing Districts": list(missing_districts)}).to_csv(missing_districts_path, index=False)

replacements = {
    "Horry County Schools"  : "Horry County School District",
    "Lake County Schools": "Lake County School District",
    "Wentzville School District": 'Wentzville R-IV School District",
    "Kirkwood School District": "Kirkwood R-VII School District",
    "Horry County Schools": "Horry County School District",
    "Sumner County Schools": "Sumner County School District",
    "Gale-Ettrick School District": "Galesville-Ettrick-Trempealeau School District",
    "North Kansas City Schools": "North Kansas City 74 School District",
    "Abington Public Schools": "Abington School District",
    "Sioux Valley School District": "Sioux Valley School District 05-5",
    "Natrona County Schools": "Natrona County School District 1"
}
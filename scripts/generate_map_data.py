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

# Manual replacements (original dictionary)
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
    "Natrona County Schools": "Natrona County School District 1",
    "King George County School District": "King George County Public Schools",
    "Williston Basin School District #7": "Williston Basin Public School District 7",
    "Hillsborough County Public Schools": "Hillsborough County School District",
    "Escambia County Public Schools": "Escambia County School District",
    "Volusia County Schools": "Volusia County School District"
}

# Load additional replacements from district_word_matches.csv
try:
    print("Loading district word matches...")
    matches_df = pd.read_csv("./data/district_word_matches.csv")
    
    # Convert matches to dictionary format
    csv_replacements = {}
    for _, row in matches_df.iterrows():
        missing_district = row['missing_district']
        potential_match = row['match']
        
        if pd.notna(missing_district) and pd.notna(potential_match):
            csv_replacements[missing_district] = potential_match
    
    # Merge with existing replacements (manual ones take precedence)
    all_replacements = {**csv_replacements, **replacements}
    
    print(f"Loaded {len(csv_replacements)} additional district mappings from CSV")
    print(f"Total district mappings: {len(all_replacements)}")
    
except FileNotFoundError:
    print("district_word_matches.csv not found, using only manual replacements")
    all_replacements = replacements

# Clean district names and apply replacements
csv_data["District"] = csv_data["District"].str.strip()
csv_data["District"] = csv_data["District"].replace(all_replacements)

# Calculate ban counts
district_ban_counts = csv_data["District"].value_counts().to_dict()

# Initialize ban counts in geojson
geojson_data["ban_count"] = 0

# Update ban counts
matched_districts = 0
total_bans_assigned = 0

for index, row in geojson_data.iterrows():
    district_name = row["NAME"]
    
    if district_name in district_ban_counts:
        ban_count = district_ban_counts[district_name]
        geojson_data.at[index, "ban_count"] = ban_count
        matched_districts += 1
        total_bans_assigned += ban_count

print(f"\nResults:")
print(f"Matched {matched_districts} districts with {total_bans_assigned} total bans")
print(f"Coverage: {(matched_districts / len(geojson_data)) * 100:.1f}% of geojson districts have data")

# Save the updated geojson
output_file = "districts_with_ban_counts.geojson"
geojson_data.to_file(output_file, driver='GeoJSON')
print(f"Saved enhanced geojson to {output_file}")

# Save summary statistics
summary = {
    "total_geojson_districts": len(geojson_data),
    "matched_districts": matched_districts,
    "total_bans": total_bans_assigned,
    "coverage_percentage": (matched_districts / len(geojson_data)) * 100
}

with open("district_matching_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Summary saved to district_matching_summary.json")
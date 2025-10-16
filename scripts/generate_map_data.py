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

# Manual replacements
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

# Function to normalize district names
def normalize_district_name(district_name, geojson_districts):
    """Try to find a matching district using various name transformations"""
    
    # First check exact match
    if district_name in geojson_districts:
        return district_name
    
    # Try manual replacements first
    if district_name in replacements:
        manual_replacement = replacements[district_name]
        if manual_replacement in geojson_districts:
            return manual_replacement
    
    # Try automatic transformations
    transformations = [
        # Replace "Public Schools" with "School District"
        lambda name: name.replace("Public Schools", "School District"),
        
        # Replace "Schools" with "School District" 
        lambda name: name.replace(" Schools", " School District"),
        
        # Replace "School District" with "Public Schools"
        lambda name: name.replace("School District", "Public Schools"),
        
        # Replace "School District" with "Schools"
        lambda name: name.replace(" School District", " Schools"),
        
        # Add "Public" before "Schools"
        lambda name: name.replace(" Schools", " Public Schools"),
        
        # Remove "Public" 
        lambda name: name.replace("Public ", ""),
        
        # Try with/without "County"
        lambda name: name.replace("County ", "") if "County" in name else name + " County",
        
        # Try adding/removing numbers and dashes
        lambda name: name.replace(" #", " ").replace("#", " "),
        
        # Try with "ISD" (Independent School District)
        lambda name: name.replace("School District", "ISD"),
    ]
    
    for transform in transformations:
        try:
            transformed_name = transform(district_name)
            if transformed_name in geojson_districts:
                return transformed_name
        except:
            continue
    
    # No match found
    return None

# Clean district names
csv_data["District"] = csv_data["District"].str.strip()

# Get geojson district names for matching
geojson_districts = set(geojson_data["NAME"].dropna().unique())

# Create normalized district mapping
print("Normalizing district names...")
district_mapping = {}
matched_count = 0
total_districts = csv_data["District"].dropna().nunique()

for district in csv_data["District"].dropna().unique():
    normalized = normalize_district_name(district, geojson_districts)
    district_mapping[district] = normalized
    if normalized and normalized != district:
        matched_count += 1
        print(f"  ✅ Matched: '{district}' → '{normalized}'")

print(f"Successfully matched {matched_count} additional districts")

# Apply normalization
csv_data["District_Normalized"] = csv_data["District"].map(district_mapping).fillna(csv_data["District"])

# Calculate ban counts using normalized names
district_ban_counts = csv_data["District_Normalized"].value_counts().to_dict()

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

print(f"\nMatched {matched_districts} districts with {total_bans_assigned} total bans")
print(f"Coverage: {(matched_districts / len(geojson_data)) * 100:.1f}% of geojson districts have data")

# Save the updated geojson
output_file = "districts_with_ban_counts.geojson"
geojson_data.to_file(output_file, driver='GeoJSON')
print(f"Saved enhanced geojson to {output_file}")

# Save summary statistics
summary = {
    "total_csv_districts": total_districts,
    "total_geojson_districts": len(geojson_data),
    "matched_districts": matched_districts,
    "total_bans": total_bans_assigned,
    "coverage_percentage": (matched_districts / len(geojson_data)) * 100
}

with open("district_matching_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nSummary saved to district_matching_summary.json")
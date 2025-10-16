import pandas as pd
import geopandas as gpd

# Load both CSV files
csv_paths = [
    "./PenAmericaData/PEN America's Index of School Book Bans (July 1, 2022 - June 30, 2023) - Sorted by Author & Title.csv",
    "./PenAmericaData/Pen America's Index of School Books Bans 2024 2025.csv"
]

# Combine CSV data
csv_data = pd.concat([pd.read_csv(path) for path in csv_paths], ignore_index=True)

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
    "Natrona County Schools": "Natrona County School District 1"
}

# Function to try automatic name normalization
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

# Load both GeoJSON files and collect all districts
geojson_paths = [
    "./geojson/School_District_Composites_SY_2023-24_TL_24.geojson",
    "./geojson/School_District_Characteristics_-_Current.geojson"
]

all_geojson_districts = set()

for geojson_path in geojson_paths:
    try:
        geojson_data = gpd.read_file(geojson_path)
        print(f"\nColumns in {geojson_path}:")
        print(geojson_data.columns.tolist())
        
        # Try different possible district name columns
        district_column = None
        for col in ['LEA_NAME', 'NAME', 'DISTRICT_NAME', 'DISTNAME', 'District']:
            if col in geojson_data.columns:
                district_column = col
                break
        
        if district_column:
            geojson_districts = set(geojson_data[district_column].dropna().unique())
            all_geojson_districts.update(geojson_districts)
            print(f"Found {len(geojson_districts)} districts in {geojson_path} using column '{district_column}'")
        else:
            print(f"No district name column found in {geojson_path}")
            
    except Exception as e:
        print(f"Error loading {geojson_path}: {e}")

print(f"\nTotal unique districts in all geojson files: {len(all_geojson_districts)}")

# Get unique districts from CSV
csv_districts = set(csv_data["District"].dropna().str.strip().unique())
print(f"Total unique districts in CSV files: {len(csv_districts)}")

# Try to match each CSV district
matched_districts = set()
manual_matches = set()
auto_matches = set()
truly_missing = set()

print(f"\nAttempting to match {len(csv_districts)} districts...")

for district in csv_districts:
    matched_name = normalize_district_name(district, all_geojson_districts)
    
    if matched_name:
        matched_districts.add(district)
        if district in replacements:
            manual_matches.add(district)
        elif matched_name != district:
            auto_matches.add(district)
            print(f"  ✅ Auto-matched: '{district}' → '{matched_name}'")
    else:
        truly_missing.add(district)

# Results summary
print(f"\n" + "="*80)
print("MATCHING RESULTS SUMMARY")
print("="*80)
print(f"Total CSV districts: {len(csv_districts)}")
print(f"Exact matches: {len(csv_districts & all_geojson_districts)}")
print(f"Manual replacements matched: {len(manual_matches)}")
print(f"Auto-transformations matched: {len(auto_matches)}")
print(f"Total matched: {len(matched_districts)}")
print(f"Still missing: {len(truly_missing)}")
print(f"Coverage: {(len(matched_districts) / len(csv_districts)) * 100:.1f}%")

# Show truly missing districts
print(f"\nDistricts still missing after all transformations ({len(truly_missing)} total):")
print("=" * 60)
for district in sorted(truly_missing)[:20]:  # Show first 20
    print(district)

if len(truly_missing) > 20:
    print(f"... and {len(truly_missing) - 20} more")

# Save results
with open("truly_missing_districts.txt", "w") as f:
    f.write("Districts still missing after all transformations:\n")
    f.write("=" * 60 + "\n")
    for district in sorted(truly_missing):
        f.write(district + "\n")

print(f"\nTruly missing districts saved to 'truly_missing_districts.txt'")
import pandas as pd
import json

csv_paths = [
    "PenAmericaData/PEN America's Index of School Book Bans (July 1, 2022 - June 30, 2023) - Sorted by Author & Title.csv",
    "PenAmericaData/Pen America's Index of School Books Bans 2024 2025.csv"
]
csv_data = pd.concat([pd.read_csv(path, usecols=["Title", "Author", "State", "District", "Date of Challenge/Removal", "Ban Status"]) for path in csv_paths], ignore_index=True)

# Replace NaN values with defaults
csv_data = csv_data.fillna({
    "Title": "Unknown",
    "Author": "Unknown",
    "State": "Unknown",
    "District": "Unknown",
    "Date of Challenge/Removal": "Unknown",
    "Ban Status": "Unknown",
})

# Calculate Ban Count for each book, author, district, and state
book_ban_counts = csv_data["Title"].value_counts().to_dict()
author_ban_counts = csv_data["Author"].value_counts().to_dict()
district_ban_counts = csv_data["District"].value_counts().to_dict()
state_ban_counts = csv_data["State"].value_counts().to_dict()

# Extract relevant fields and group related rows
search_data = {}

for _, row in csv_data.iterrows():
    # Add book title
    if pd.notna(row["Title"]):
        key = f"book:{row['Title']}"
        if key not in search_data:
            search_data[key] = {
                "type": "book",
                "value": row["Title"],
                "ban_count": book_ban_counts.get(row["Title"], 0),
                "details": []
            }
        search_data[key]["details"].append({
            "author": row["Author"],
            "state": row["State"],
            "district": row["District"],
            "date_of_challenge": row["Date of Challenge/Removal"],
            "ban_status": row["Ban Status"],
        })

    # Add author
    if pd.notna(row["Author"]):
        key = f"author:{row['Author']}"
        if key not in search_data:
            search_data[key] = {
                "type": "author",
                "value": row["Author"],
                "ban_count": author_ban_counts.get(row["Author"], 0),
                "details": []
            }
        search_data[key]["details"].append({
            "book": row["Title"],
            "state": row["State"],
            "district": row["District"],
            "date_of_challenge": row["Date of Challenge/Removal"],
            "ban_status": row["Ban Status"],
        })

    # Add district
    if pd.notna(row["District"]):
        key = f"district:{row['District']}"
        if key not in search_data:
            search_data[key] = {
                "type": "district",
                "value": row["District"],
                "ban_count": district_ban_counts.get(row["District"], 0),
                "details": []
            }
        search_data[key]["details"].append({
            "book": row["Title"],
            "author": row["Author"],
            "state": row["State"],
            "date_of_challenge": row["Date of Challenge/Removal"],
            "ban_status": row["Ban Status"],
        })

    # Add state
    if pd.notna(row["State"]):
        key = f"state:{row['State']}"
        if key not in search_data:
            search_data[key] = {
                "type": "state",
                "value": row["State"],
                "ban_count": state_ban_counts.get(row["State"], 0),
                "details": []
            }
        search_data[key]["details"].append({
            "book": row["Title"],
            "author": row["Author"],
            "district": row["District"],
            "date_of_challenge": row["Date of Challenge/Removal"],
            "ban_status": row["Ban Status"],
        })

# Convert to a list and save to JSON
search_data_list = list(search_data.values())
output_path = "search_data.json"
with open(output_path, "w") as json_file:
    json.dump(search_data_list, json_file, indent=2)

print(f"Search data saved to {output_path}")
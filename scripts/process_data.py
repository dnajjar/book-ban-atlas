import pandas as pd
import json

# Load your CSV data
csv_paths = [
    "./PenAmericaData/PEN America's Index of School Book Bans (July 1, 2022 - June 30, 2023) - Sorted by Author & Title.csv",
    "./PenAmericaData/Pen America's Index of School Books Bans 2024 2025.csv"
]
csv_data = pd.concat([pd.read_csv(path) for path in csv_paths], ignore_index=True)

# Fill NaN values
csv_data = csv_data.fillna({
    "Title": "Unknown",
    "Author": "Unknown", 
    "State": "Unknown",
    "District": "Unknown",
    "Date of Challenge/Removal": "Unknown",
    "Ban Status": "Unknown",
})

# Calculate statistics for each author
author_stats = {}
for author in csv_data['Author'].unique():
    if author != "Unknown":
        author_data = csv_data[csv_data['Author'] == author]
        
        # Count unique books by this author that are banned
        unique_books = author_data['Title'].nunique()
        
        # Count total ban instances (same book can be banned multiple times)
        total_bans = len(author_data)
        
        # Count states where author's books are banned
        states_with_bans = author_data['State'].nunique()
        
        # Count districts where author's books are banned
        districts_with_bans = author_data['District'].nunique()
        
        # Get list of banned books by this author
        banned_books = author_data['Title'].unique().tolist()
        
        author_stats[author] = {
            'unique_books_banned': unique_books,
            'total_ban_instances': total_bans,
            'states_with_bans': states_with_bans,
            'districts_with_bans': districts_with_bans,
            'banned_books': banned_books
        }

# Rest of your existing processing code...
search_data = {}

for _, row in csv_data.iterrows():
    # Add book title
    if pd.notna(row["Title"]):
        key = f"book:{row['Title']}"
        if key not in search_data:
            search_data[key] = {
                "type": "book",
                "value": row["Title"],
                "details": []
            }
        search_data[key]["details"].append({
            "book": row["Title"],
            "author": row["Author"],
            "state": row["State"],
            "district": row["District"],
            "date_of_challenge": row["Date of Challenge/Removal"],
            "ban_status": row["Ban Status"],
        })

    # Add author with statistics
    if pd.notna(row["Author"]):
        key = f"author:{row['Author']}"
        if key not in search_data:
            search_data[key] = {
                "type": "author",
                "value": row["Author"],
                "author_stats": author_stats.get(row["Author"], {}),  # Add author stats
                "details": []
            }
        search_data[key]["details"].append({
            "book": row["Title"],
            "author": row["Author"],
            "state": row["State"],
            "district": row["District"],
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
                "details": []
            }
        search_data[key]["details"].append({
            "book": row["Title"],
            "author": row["Author"],
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
                "details": []
            }
        search_data[key]["details"].append({
            "book": row["Title"],
            "author": row["Author"],
            "state": row["State"],
            "district": row["District"],
            "date_of_challenge": row["Date of Challenge/Removal"],
            "ban_status": row["Ban Status"],
        })

# Convert to list and save
search_data_list = list(search_data.values())
with open("search_data.json", "w") as json_file:
    json.dump(search_data_list, json_file, indent=2)

print("Data processing complete with author statistics!")
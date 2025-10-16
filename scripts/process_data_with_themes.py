import pandas as pd
import json
import numpy as np

# Helper function to clean values for JSON serialization
def clean_for_json(value):
    if pd.isna(value) or value is None or value == 'nan' or str(value).lower() == 'nan':
        return ''
    return str(value)

# Load your CSV data
csv_paths = [
    "./PenAmericaData/PEN America's Index of School Book Bans (July 1, 2022 - June 30, 2023) - Sorted by Author & Title.csv",
    "./PenAmericaData/Pen America's Index of School Books Bans 2024 2025.csv"
]
csv_data = pd.concat([pd.read_csv(path) for path in csv_paths], ignore_index=True)

# Try to load enhanced data with themes and descriptions
try:
    enhanced_csv_path = "./enhanced_book_bans_combined.csv"
    enhanced_data = pd.read_csv(enhanced_csv_path)
    print(f"Loaded enhanced data with {len(enhanced_data)} records")
    
    # Create a mapping of book titles to themes and descriptions
    book_enhancements = {}
    for _, row in enhanced_data.iterrows():
        if pd.notna(row.get('Title')):
            key = str(row['Title']).strip()
            book_enhancements[key] = {
                'themes': str(row.get('themes', '')) if pd.notna(row.get('themes')) else '',
                'description': str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                'cover_url': str(row.get('cover_url', '')) if pd.notna(row.get('cover_url')) else '',
                'work_id': str(row.get('work_id', '')) if pd.notna(row.get('work_id')) else '',
                'isbn': str(row.get('isbn', '')) if pd.notna(row.get('isbn')) else ''
            }
    
    print(f"Created enhancement mapping for {len(book_enhancements)} books")
    
except FileNotFoundError:
    print("Enhanced data file not found. Proceeding without themes and descriptions.")
    book_enhancements = {}

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

# Extract relevant fields and group related rows
search_data = {}

for _, row in csv_data.iterrows():
    # Get book enhancements if available
    book_title = str(row["Title"]).strip()
    enhancements = book_enhancements.get(book_title, {})
    
    # Create base detail record with enhancements - clean all values
    base_detail = {
        "book": clean_for_json(row["Title"]),
        "author": clean_for_json(row["Author"]),
        "state": clean_for_json(row["State"]),
        "district": clean_for_json(row["District"]),
        "date_of_challenge": clean_for_json(row["Date of Challenge/Removal"]),
        "ban_status": clean_for_json(row["Ban Status"]),
        "themes": clean_for_json(enhancements.get('themes', '')),
        "description": clean_for_json(enhancements.get('description', '')),
        "cover_url": clean_for_json(enhancements.get('cover_url', '')),
        "work_id": clean_for_json(enhancements.get('work_id', '')),
        "isbn": clean_for_json(enhancements.get('isbn', ''))
    }
    
    # ADD THEMES AS SEARCHABLE ITEMS
    themes_list = enhancements.get('themes', '')
    if themes_list and themes_list.strip():
        # Split themes by comma and create search entries for each theme
        individual_themes = [theme.strip() for theme in themes_list.split(',') if theme.strip()]
        
        for theme in individual_themes:
            theme_key = f"theme:{theme}"
            if theme_key not in search_data:
                search_data[theme_key] = {
                    "type": "theme",
                    "value": theme,
                    "details": []
                }
            search_data[theme_key]["details"].append(base_detail.copy())
    
    # Add book title
    if pd.notna(row["Title"]):
        key = f"book:{row['Title']}"
        if key not in search_data:
            search_data[key] = {
                "type": "book",
                "value": clean_for_json(row["Title"]),
                "details": []
            }
        search_data[key]["details"].append(base_detail.copy())

    # Add author with statistics
    if pd.notna(row["Author"]):
        key = f"author:{row['Author']}"
        if key not in search_data:
            search_data[key] = {
                "type": "author",
                "value": clean_for_json(row["Author"]),
                "author_stats": author_stats.get(row["Author"], {}),
                "details": []
            }
        search_data[key]["details"].append(base_detail.copy())

    # Add state
    if pd.notna(row["State"]):
        key = f"state:{row['State']}"
        if key not in search_data:
            search_data[key] = {
                "type": "state",
                "value": clean_for_json(row["State"]),
                "details": []
            }
        search_data[key]["details"].append(base_detail.copy())

    # Add district
    if pd.notna(row["District"]):
        key = f"district:{row['District']}"
        if key not in search_data:
            search_data[key] = {
                "type": "district",
                "value": clean_for_json(row["District"]),
                "details": []
            }
        search_data[key]["details"].append(base_detail.copy())

# Convert to list and save
search_data_list = list(search_data.values())

# Print summary
total_records = len(search_data_list)
records_with_themes = sum(1 for item in search_data_list 
                         if any(detail.get('themes') and detail.get('themes').strip() 
                               for detail in item['details']))

# Count theme records specifically
theme_records = sum(1 for item in search_data_list if item.get('type') == 'theme')

print(f"\nProcessing Summary:")
print(f"Total search records: {total_records}")
print(f"Theme search records: {theme_records}")
print(f"Records with theme data: {records_with_themes}")
print(f"Enhancement coverage: {(records_with_themes/total_records)*100:.1f}%")

# Show some example themes
print(f"\nExample themes created:")
theme_examples = [item['value'] for item in search_data_list if item.get('type') == 'theme'][:10]
for theme in theme_examples:
    print(f"  🏷️ {theme}")

# Use custom JSON encoder to handle any remaining issues
class CleanJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return '""'
        return super().encode(obj)

with open("search_data.json", "w") as json_file:
    json.dump(search_data_list, json_file, indent=2, cls=CleanJSONEncoder)

print("Data processing complete with themes and descriptions!")
print("Enhanced search_data.json created successfully.")
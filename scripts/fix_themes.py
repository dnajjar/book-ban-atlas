import json
import re

# Load the search data
with open('./data/search_data.json', 'r') as f:
    search_data = json.load(f)

print("Fixing themes in search_data.json...")

# Function to check if "meth" appears as substring (not whole word)
def has_meth_substring_only(text):
    """Check if 'meth' appears as substring but not as whole word"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check if 'meth' appears in text
    if 'meth' not in text_lower:
        return False
    
    # Check if it's NOT a whole word (i.e., it's part of another word)
    pattern = r'\bmeth\b'
    whole_word_matches = re.findall(pattern, text_lower)
    
    # If 'meth' exists in text but NOT as whole word, it's a substring
    return len(whole_word_matches) == 0

# Track changes
fixed_count = 0
total_substance_abuse_records = 0

# Process each item in search data
for item in search_data:
    for detail in item.get('details', []):
        themes = detail.get('themes', '')
        
        if 'Substance Abuse' in themes:
            total_substance_abuse_records += 1
            
            # Check description and themes for substring "meth"
            description = detail.get('description', '')
            combined_text = f"{themes} {description}"
            
            if has_meth_substring_only(combined_text):
                print(f"Fixing: '{detail.get('book', 'Unknown')}' - removing Substance Abuse theme")
                print(f"  Reason: Found 'meth' as substring in: {combined_text[:100]}...")
                
                # Remove "Substance Abuse" from themes
                theme_list = [theme.strip() for theme in themes.split(',') if theme.strip()]
                theme_list = [theme for theme in theme_list if theme != 'Substance Abuse']
                detail['themes'] = ', '.join(theme_list)
                
                fixed_count += 1

# Also remove "Substance Abuse" theme entries that were incorrectly created
theme_items_to_remove = []
for i, item in enumerate(search_data):
    if item.get('type') == 'theme' and item.get('value') == 'Substance Abuse':
        # Check if any of the details have meth substring issues
        has_false_positives = False
        for detail in item.get('details', []):
            description = detail.get('description', '')
            combined_text = f"{detail.get('themes', '')} {description}"
            if has_meth_substring_only(combined_text):
                has_false_positives = True
                break
        
        if has_false_positives:
            # Remove the entire theme entry if it has false positives
            theme_items_to_remove.append(i)

# Remove theme items in reverse order to maintain indices
for i in reversed(theme_items_to_remove):
    removed_item = search_data.pop(i)
    print(f"Removed theme entry: {removed_item.get('value')} with {len(removed_item.get('details', []))} details")

# Save the fixed data
with open('./data/search_data.json', 'w') as f:
    json.dump(search_data, f, indent=2)

print(f"\nSummary:")
print(f"Total records with Substance Abuse theme: {total_substance_abuse_records}")
print(f"Records fixed (theme removed): {fixed_count}")
print(f"Theme entries removed: {len(theme_items_to_remove)}")
print("✅ search_data.json has been updated!")
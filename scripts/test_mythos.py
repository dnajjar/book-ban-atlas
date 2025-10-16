from bookinfo import BookInfoEnhancer

# Create enhancer instance with debug
enhancer = BookInfoEnhancer()

# Temporarily override the _extract_themes_from_text method with debug logging
def debug_extract_themes_from_text(self, text: str):
    themes = set()
    theme_keywords = self._get_theme_keywords()
    text_lower = text.lower()
    
    print(f"DEBUG: Analyzing text: '{text_lower}'")
    print("=" * 50)
    
    for theme, keywords in theme_keywords.items():
        matched_keywords = []
        for keyword in keywords:
            if keyword in text_lower:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            themes.add(theme)
            print(f"DEBUG: Theme '{theme}' matched with keywords: {matched_keywords}")
                
    return themes

# Replace the method temporarily
enhancer._extract_themes_from_text = debug_extract_themes_from_text.__get__(enhancer, BookInfoEnhancer)

# Test data from your CSV
description = "Here are the thrills, grandeur, and unabashed fun of the Greek myths, stylishly retold by Stephen Fry. The legendary writer, actor, and comedian breathes life into ancient tales, from Pandora's box to Prometheus's fire, and transforms the adventures of Zeus and the Olympians into emotionally resonant and deeply funny stories, without losing any of their original wonder. Classical artwork inspired by the myths and learned notes from the author offer rich cultural context."

subjects = []

print("Testing Mythos theme identification with DEBUG:")
print("=" * 50)

# Test the raw text extraction
combined_text = ' '.join(subjects + [description])
themes = enhancer._extract_themes_from_text(combined_text)
print(f"\nFinal result: {themes}")
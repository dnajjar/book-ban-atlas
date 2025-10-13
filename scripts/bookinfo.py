import requests
import json
import time
import re
from typing import Dict, List, Optional

class BookInfoEnhancer:
    def __init__(self, isbndb_api_key: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BookBanAtlas/1.0 (https://example.com/contact)'
        })
        self.isbndb_api_key = isbndb_api_key
        self.cache = {}
        
    def get_isbn_from_isbndb(self, title: str, author: str) -> Optional[str]:
        """Get ISBN from ISBNdb API"""
        if not self.isbndb_api_key:
            return None
            
        try:
            url = "https://api2.isbndb.com/books/"
            headers = {
                'Authorization': self.isbndb_api_key
            }
            params = {
                'title': title,
                'author': author,
                'page': 1,
                'pageSize': 1
            }
            
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('books') and len(data['books']) > 0:
                return data['books'][0].get('isbn13') or data['books'][0].get('isbn')
                
            return None
            
        except Exception as e:
            print(f"Error fetching ISBN for '{title}' by {author}: {e}")
            return None
    
    def get_book_info(self, title: str, author: str) -> Optional[Dict]:
        """Fetch book information from OpenLibrary API with ISBN lookup"""
        cache_key = f"{title.lower().strip()}-{author.lower().strip()}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            # First try to get ISBN from ISBNdb
            isbn = self.get_isbn_from_isbndb(title, author)
            
            # Search OpenLibrary - try ISBN first if we have it
            if isbn:
                # Search by ISBN
                search_url = f"https://openlibrary.org/search.json?isbn={isbn}&limit=1"
            else:
                # Search by title and author
                search_url = f"https://openlibrary.org/search.json?title={title}&author={author}&limit=1"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            search_data = response.json()
            
            if not search_data.get('docs'):
                self.cache[cache_key] = None
                return None
                
            book = search_data['docs'][0]
            
            # Get work details if available
            work_key = book.get('key')
            description = "No description available"
            
            if work_key:
                work_url = f"https://openlibrary.org{work_key}.json"
                work_response = self.session.get(work_url)
                
                if work_response.status_code == 200:
                    work_data = work_response.json()
                    desc = work_data.get('description')
                    if isinstance(desc, dict):
                        description = desc.get('value', description)
                    elif isinstance(desc, str):
                        description = desc
            
            # Use the ISBN we found or the one from OpenLibrary
            final_isbn = isbn or (book.get('isbn', [None])[0] if book.get('isbn') else None)
            
            book_info = {
                'title': book.get('title', title),
                'author': book.get('author_name', [author])[0] if book.get('author_name') else author,
                'description': self.clean_description(description),
                'subjects': book.get('subject', []),
                'publish_year': book.get('first_publish_year'),
                'cover_url': f"https://covers.openlibrary.org/b/id/{book['cover_i']}-M.jpg" if book.get('cover_i') else None,
                'isbn': final_isbn,
                'isbn13': final_isbn if final_isbn and len(final_isbn) == 13 else None,
                'isbn10': final_isbn if final_isbn and len(final_isbn) == 10 else None
            }
            
            self.cache[cache_key] = book_info
            time.sleep(0.2)  # Be respectful to APIs
            return book_info
            
        except Exception as e:
            print(f"Error fetching info for '{title}' by {author}: {e}")
            self.cache[cache_key] = None
            return None
    
    def clean_description(self, description: str) -> str:
        """Clean and truncate description"""
        if not description or description == "No description available":
            return description
            
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        
        # Truncate if too long
        if len(description) > 500:
            description = description[:500] + "..."
            
        return description.strip()
    
    def identify_themes(self, subjects: List[str], description: str) -> List[str]:
        """Identify common themes from subjects and description"""
        themes = []
        theme_keywords = {
            'LGBTQ+': ['lgbt', 'gay', 'lesbian', 'transgender', 'queer', 'homosexual', 'gender identity', 'sexual orientation'],
            'Race & Racism': ['race', 'racism', 'slavery', 'civil rights', 'discrimination', 'african american', 'black history', 'prejudice'],
            'Sexual Content': ['sex', 'sexual', 'sexuality', 'romance', 'intimate', 'adult content', 'mature'],
            'Violence': ['violence', 'war', 'death', 'murder', 'abuse', 'domestic violence', 'assault'],
            'Religion': ['religion', 'god', 'christian', 'islam', 'jewish', 'faith', 'bible', 'religious'],
            'Mental Health': ['depression', 'suicide', 'mental health', 'anxiety', 'trauma', 'self-harm', 'eating disorder'],
            'Politics': ['politics', 'government', 'democracy', 'election', 'political', 'activism', 'protest'],
            'Coming of Age': ['teenager', 'adolescent', 'growing up', 'youth', 'high school', 'young adult', 'teen'],
            'Family Issues': ['family', 'divorce', 'adoption', 'abuse', 'neglect', 'family problems'],
            'Substance Abuse': ['drugs', 'alcohol', 'addiction', 'substance abuse', 'drinking'],
            'Social Issues': ['poverty', 'homelessness', 'bullying', 'social justice', 'inequality']
        }
        
        # Combine all text for analysis
        all_text = ' '.join(subjects + [description]).lower()
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def enhance_search_data(self, input_file: str, output_file: str):
        """Enhance the search data JSON with book information"""
        print("Loading search data...")
        with open(input_file, 'r') as f:
            search_data = json.load(f)
        
        total_books = set()
        for item in search_data:
            for detail in item.get('details', []):
                total_books.add((detail.get('book', ''), detail.get('author', '')))
        
        print(f"Found {len(total_books)} unique books to enhance...")
        
        # Process each item in search data
        for i, item in enumerate(search_data):
            print(f"Processing item {i+1}/{len(search_data)}: {item.get('value', 'Unknown')}")
            
            for detail in item.get('details', []):
                book_title = detail.get('book', '')
                author = detail.get('author', '')
                
                if book_title and author:
                    book_info = self.get_book_info(book_title, author)
                    
                    if book_info:
                        detail['description'] = book_info['description']
                        detail['themes'] = self.identify_themes(book_info['subjects'], book_info['description'])
                        detail['cover_url'] = book_info['cover_url']
                        detail['publish_year'] = book_info['publish_year']
                        detail['isbn'] = book_info['isbn']
                        detail['isbn13'] = book_info['isbn13']
                        detail['isbn10'] = book_info['isbn10']
                    else:
                        detail['description'] = "No description available"
                        detail['themes'] = []
                        detail['cover_url'] = None
        
        # Save enhanced data
        print(f"Saving enhanced data to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(search_data, f, indent=2)
        
        print("Enhancement complete!")

if __name__ == "__main__":
    # You'll need to get an API key from https://isbndb.com/
    API_KEY = "YOUR_ISBNDB_API_KEY_HERE"  # Replace with your actual key
    
    enhancer = BookInfoEnhancer(isbndb_api_key=API_KEY)
    enhancer.enhance_search_data('search_data.json', 'search_data_enhanced.json')
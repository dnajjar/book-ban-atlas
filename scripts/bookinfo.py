import requests
import json
import time
import re
import pandas as pd
from typing import Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class BookInfoEnhancer:
    """Enhanced book information retrieval and theme identification system."""
    
    def __init__(self, max_workers: int = 10, requests_per_second: int = 5):
        """
        Initialize the BookInfoEnhancer with session and cache.
        
        Args:
            max_workers: Maximum number of concurrent threads
            requests_per_second: Rate limit for API requests
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BookBanAtlas/1.0 (https://example.com/contact)'
        })
        self.cache = {}
        self.max_workers = max_workers
        self.rate_limit = 1.0 / requests_per_second  # Delay between requests
        self.last_request_time = {}
        self.lock = threading.Lock()
    
    def _rate_limit_request(self):
        """Implement rate limiting for API requests."""
        with self.lock:
            thread_id = threading.current_thread().ident
            current_time = time.time()
            
            if thread_id in self.last_request_time:
                time_since_last = current_time - self.last_request_time[thread_id]
                if time_since_last < self.rate_limit:
                    time.sleep(self.rate_limit - time_since_last)
            
            self.last_request_time[thread_id] = time.time()
        
    def _get_theme_keywords(self) -> Dict[str, List[str]]:
        """
        Get content-based theme keywords for classification.
        Focuses on book content rather than author identity.
        
        Returns:
            Dict mapping theme names to lists of identifying keywords
        """
        return {
            'LGBTQ+': [
                # Direct terms about identity and relationships
                'lgbt', 'gay', 'lesbian', 'transgender', 'queer', 'homosexual', 'bisexual',
                'gender identity', 'sexual orientation', 'same-sex', 'two-spirit', 'nonbinary',
                'coming out', 'closet', 'pride', 'rainbow', 'gender dysphoria',
                # Content-based title patterns
                'simon vs', 'aristotle and dante', 'cemetery boys', 'felix ever after',
                'last night at the telegraph club', 'you should see me in a crown',
                'the miseducation of cameron post', 'king and the dragonflies'
            ],
            
            'Race & Racism': [
                # Direct terms about racial issues
                'race', 'racism', 'slavery', 'civil rights', 'discrimination', 'prejudice',
                'african american', 'black history', 'jim crow', 'segregation', 'lynch',
                'white supremacy', 'racial injustice', 'police brutality', 'racial profiling',
                'plantation', 'confederate', 'kkk', 'apartheid', 'ethnic cleansing',
                # Content-based title patterns
                'the hate u give', 'dear martin', 'all american boys', 'ghost boys',
                'new kid', 'stamped', 'brown girl dreaming', 'the crossover'
            ],
            
            'Hispanic & Latino': [
                # Cultural and identity terms
                'hispanic', 'latino', 'latina', 'latinx', 'chicano', 'chicana',
                'mexican american', 'puerto rican', 'cuban american', 'central american',
                'south american', 'spanish speaking', 'bilingual', 'immigration',
                'border crossing', 'undocumented', 'deportation', 'migrant',
                'día de los muertos', 'quinceañera', 'barrio', 'mestizo'
            ],
            
            'Asian': [
                # Cultural and identity terms
                'asian', 'asian american', 'chinese', 'japanese', 'korean', 'vietnamese',
                'filipino', 'thai', 'indian', 'pakistani', 'bangladeshi', 'cambodian',
                'hmong', 'pacific islander', 'immigrant', 'asian culture',
                'confucianism', 'buddhism', 'hinduism', 'martial arts', 'chopsticks',
                'rice', 'sushi', 'dim sum', 'lunar new year'
            ],
            
            'African': [
                # African culture and diaspora
                'african', 'africa', 'nigerian', 'ghanaian', 'kenyan', 'ethiopian',
                'south african', 'moroccan', 'egyptian', 'african american',
                'diaspora', 'colonialism', 'apartheid', 'tribal', 'safari',
                'ubuntu', 'swahili', 'yoruba', 'akan', 'bantu'
            ],
            
            'Art': [
                # Visual arts and creativity
                'art', 'artist', 'painting', 'drawing', 'sculpture', 'photography',
                'gallery', 'museum', 'exhibition', 'canvas', 'palette', 'brush',
                'creativity', 'artistic', 'visual arts', 'fine arts', 'graphic design',
                'illustration', 'sketch', 'portrait', 'landscape', 'abstract',
                'impressionism', 'surrealism', 'cubism', 'renaissance'
            ],
            
            'Poetry': [
                # Poetry and verse
                'poetry', 'poem', 'poet', 'verse', 'rhyme', 'meter', 'sonnet',
                'haiku', 'ballad', 'epic', 'lyric', 'free verse', 'spoken word',
                'slam poetry', 'anthology', 'stanza', 'metaphor', 'alliteration',
                'poetic', 'verses', 'recitation', 'literary'
            ],
            
            'Sexual Content': [
                'sex', 'sexual', 'sexuality', 'romance', 'intimate', 'adult content',
                'mature', 'erotic', 'passion', 'desire', 'seduction', 'affair',
                'pregnancy', 'contraception', 'sexual education', 'puberty',
                'fifty shades', 'court of', 'throne of glass'
            ],
            
            'Violence': [
                'violence', 'war', 'death', 'murder', 'abuse', 'domestic violence',
                'assault', 'rape', 'torture', 'genocide', 'holocaust', 'killing',
                'blood', 'brutal', 'savage', 'massacre', 'terrorism', 'bombing',
                'gun violence', 'school shooting', 'suicide bombing'
            ],
            
            'Religion': [
                'religion', 'god', 'christian', 'islam', 'jewish', 'faith', 'bible',
                'religious', 'church', 'mosque', 'synagogue', 'prayer', 'divine',
                'sacred', 'spiritual', 'atheist', 'atheism', 'evangelical',
                'fundamentalist', 'missionary', 'prophet', 'salvation'
            ],
            
            'Mental Health': [
                'depression', 'suicide', 'mental health', 'anxiety', 'trauma',
                'self-harm', 'eating disorder', 'ptsd', 'bipolar', 'schizophrenia',
                'therapy', 'counseling', 'medication', 'psychiatric', 'psychologist',
                'cutting', 'anorexia', 'bulimia', 'panic attack',
                'thirteen reasons why', 'it\'s kind of a funny story'
            ],
            
            'Politics': [
                'politics', 'government', 'democracy', 'election', 'political',
                'activism', 'protest', 'revolution', 'conservative', 'liberal',
                'fascism', 'communism', 'socialism', 'capitalism', 'dictator',
                'totalitarian', 'authoritarian', 'propaganda', 'censorship'
            ],
            
            'Coming of Age': [
                'teenager', 'adolescent', 'growing up', 'youth', 'high school',
                'young adult', 'teen', 'puberty', 'first love', 'identity',
                'self-discovery', 'finding yourself', 'teenage rebellion',
                'perks of being a wallflower'
            ],
            
            'Family Dysfunction': [
                'family', 'divorce', 'adoption', 'abuse', 'neglect', 'family problems',
                'parents', 'mother', 'father', 'sibling', 'domestic', 'household',
                'family dysfunction', 'broken family', 'foster care', 'custody',
                'abandonment', 'family violence'
            ],
            
            'Substance Abuse': [
                'drugs', 'alcohol', 'addiction', 'substance abuse', 'drinking',
                'cocaine', 'heroin', 'marijuana', 'overdose', 'rehab', 'recovery',
                'alcoholic', 'addict', 'crank', 'meth', 'pills', 'prescription abuse',
                'detox', 'withdrawal', 'dealer', 'drug dealing'
            ],
            
            'Social Issues': [
                'poverty', 'homelessness', 'bullying', 'social justice', 'inequality',
                'class struggle', 'economic disparity', 'social problems',
                'injustice', 'oppression', 'human rights', 'social activism',
                'cyberbullying', 'discrimination', 'marginalization'
            ]
        }
    
    def _search_openlibrary(self, title: str, author: str = None) -> Optional[Dict]:
        """
        Search OpenLibrary API for book information by title and optionally author.
        Handles titles with colons by trying both full title and title before colon.
        
        Args:
            title: Book title to search for
            author: Author name to help narrow search results
            
        Returns:
            Dict with book data from OpenLibrary, or None if not found
        """
        self._rate_limit_request()  # Apply rate limiting
        
        try:
            # First try the full title with author if provided
            search_url = "https://openlibrary.org/search.json"
            params = {'title': title, 'limit': 5}  # Increased limit to find better matches
            
            if author and author != "Unknown":
                params['author'] = author
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            search_data = response.json()
            
            # If we have results, try to find the best match
            if search_data.get('docs') and len(search_data['docs']) > 0:
                books = search_data['docs']
                
                # If we have an author, try to find a book by that author
                if author and author != "Unknown":
                    for book in books:
                        book_authors = book.get('author_name', [])
                        for book_author in book_authors:
                            if author.lower() in book_author.lower() or book_author.lower() in author.lower():
                                return book
                
                # If no author match found, return the first result
                return books[0]
            
            # If no results and title has colon, try first part only
            if ':' in title:
                short_title = title.split(':')[0].strip()
                
                params = {'title': short_title, 'limit': 5}
                if author and author != "Unknown":
                    params['author'] = author
                
                self._rate_limit_request()  # Rate limit the retry too
                response = self.session.get(search_url, params=params, timeout=10)
                response.raise_for_status()
                search_data = response.json()
                
                if search_data.get('docs') and len(search_data['docs']) > 0:
                    books = search_data['docs']
                    
                    # Again, try to match by author if provided
                    if author and author != "Unknown":
                        for book in books:
                            book_authors = book.get('author_name', [])
                            for book_author in book_authors:
                                if author.lower() in book_author.lower() or book_author.lower() in author.lower():
                                    return book
                    
                    return books[0]
            
            return None
            
        except Exception as e:
            print(f"Error searching OpenLibrary for '{title}': {e}")
            return None
    
    def _get_work_details(self, work_key: str) -> Dict[str, any]:
        """
        Get detailed work information from OpenLibrary work ID.
        
        Args:
            work_key: OpenLibrary work key (e.g., "/works/OL123456W")
            
        Returns:
            Dict with description and subjects, or defaults if not found
        """
        if not work_key or not work_key.startswith('/works/'):
            return {
                'description': "No description available",
                'subjects': []
            }
            
        self._rate_limit_request()  # Apply rate limiting
        
        try:
            work_id = work_key.replace('/works/', '')
            work_url = f"https://openlibrary.org/works/{work_id}.json"
            work_response = self.session.get(work_url, timeout=10)
            
            if work_response.status_code == 200:
                work_data = work_response.json()
                
                # Get description
                desc = work_data.get('description')
                description = "No description available"
                if isinstance(desc, dict):
                    description = desc.get('value', "No description available")
                elif isinstance(desc, str):
                    description = desc
                
                # Get subjects from work data
                subjects = work_data.get('subjects', [])
                
                return {
                    'description': description,
                    'subjects': subjects
                }
                    
        except Exception as e:
            print(f"Error fetching work details for {work_key}: {e}")
            
        return {
            'description': "No description available", 
            'subjects': []
        }
    
    def _clean_description(self, description: str) -> str:
        """
        Clean and truncate book description for display.
        
        Args:
            description: Raw description text
            
        Returns:
            Cleaned and truncated description
        """
        if not description or description == "No description available":
            return description
            
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        
        # Truncate if too long
        if len(description) > 500:
            description = description[:500] + "..."
            
        return description.strip()
    
    def extract_themes_from_text(text: str) -> Set[str]:
        """
        Extract themes from text using keyword matching.
        
        Args:
            text: Text to analyze for themes
            
        Returns:
            Set of identified theme names
        """
        themes = set()
        theme_keywords = self._get_theme_keywords()
        text_lower = text.lower()
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.add(theme)
                
        return themes
    
    def identify_themes_from_subjects_and_description(self, subjects: List[str], description: str) -> List[str]:
        """
        Identify themes from OpenLibrary subjects and description.
        
        Args:
            subjects: List of subject tags from OpenLibrary
            description: Book description text
            
        Returns:
            List of identified theme names
        """
        # Combine all text for analysis
        all_text = ' '.join(subjects + [description])
        themes = self._extract_themes_from_text(all_text)
        return list(themes)
    
    def identify_themes_from_title_only(self, title: str) -> List[str]:
        """
        Identify themes from book title when description unavailable.
        
        Args:
            title: Book title
            
        Returns:
            List of identified theme names
        """
        # If title has colon, also analyze the part before colon
        titles_to_analyze = [title]
        if ':' in title:
            short_title = title.split(':')[0].strip()
            titles_to_analyze.append(short_title)
        
        # Analyze titles for themes
        text_to_analyze = ' '.join(titles_to_analyze)
        themes = self._extract_themes_from_text(text_to_analyze)
        return list(themes)
    
    def identify_themes_comprehensive(self, subjects: List[str], description: str, title: str = "") -> List[str]:
        """
        Comprehensive theme identification using all available information.
        
        Args:
            subjects: OpenLibrary subject tags
            description: Book description
            title: Book title (fallback)
            
        Returns:
            List of identified theme names
        """
        # First try subjects and description
        themes = set(self.identify_themes_from_subjects_and_description(subjects, description))
        
        # If no themes found, try title inference
        if not themes and title:
            themes.update(self.identify_themes_from_title_only(title))
        
        return list(themes)
    
    def get_book_info_from_title(self, title: str, author: str = None) -> Optional[Dict]:
        """
        Get comprehensive book information from OpenLibrary by title and author.
        
        Args:
            title: Book title to search for
            author: Author name to help narrow search results
            
        Returns:
            Dict with book information, or None if not found
        """
        cache_key = f"title_{title.lower().strip()}_author_{(author or '').lower().strip()}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Search OpenLibrary with both title and author
        book = self._search_openlibrary(title, author)
        if not book:
            self.cache[cache_key] = None
            return None
        
        # Extract work ID and get detailed work information
        work_key = book.get('key')
        work_id = None
        if work_key and work_key.startswith('/works/'):
            work_id = work_key.replace('/works/', '')
        
        # Get detailed work data (description + subjects) using work ID
        work_details = self._get_work_details(work_key) if work_key else {
            'description': "No description available",
            'subjects': []
        }
        
        # Combine subjects from search result and work details
        search_subjects = book.get('subject', [])
        work_subjects = work_details.get('subjects', [])
        all_subjects = list(set(search_subjects + work_subjects))
        
        # Use author from the OpenLibrary data (more reliable than input)
        openlibrary_author = book.get('author_name', [author or 'Unknown'])[0] if book.get('author_name') else (author or 'Unknown')
        
        book_info = {
            'title': book.get('title', title),
            'author': openlibrary_author,
            'description': self._clean_description(work_details['description']),
            'subjects': all_subjects,
            'publish_year': book.get('first_publish_year'),
            'cover_url': f"https://covers.openlibrary.org/b/id/{book['cover_i']}-M.jpg" if book.get('cover_i') else None,
            'isbn': book.get('isbn', [None])[0] if book.get('isbn') else None,
            'work_id': work_id,
            'openlibrary_key': book.get('key'),
            'openlibrary_url': f"https://openlibrary.org{book.get('key')}" if book.get('key') else None,
            'work_url': f"https://openlibrary.org/works/{work_id}" if work_id else None
        }
        
        self.cache[cache_key] = book_info
        return book_info

    def process_single_book(self, title: str, author: str) -> tuple:
        """
        Process a single book and return the result.
        This method is designed to be called concurrently.
        
        Args:
            title: Book title
            author: Author name
            
        Returns:
            Tuple of (title, book_info_dict)
        """
        if title == "Unknown":
            return title, None
            
        try:
            book_info = self.get_book_info_from_title(title, author)
            
            if book_info:
                # Use comprehensive theme identification
                themes = self.identify_themes_comprehensive(
                    book_info['subjects'], 
                    book_info['description'],
                    title
                )
                book_info['themes'] = themes
                return title, book_info
            else:
                # If no book info found, still try to infer themes from title
                themes = self.identify_themes_from_title_only(title)
                book_info = {
                    'title': title,
                    'author': author,
                    'description': "No description available",
                    'themes': themes,
                    'subjects': [],
                    'publish_year': None,
                    'cover_url': None,
                    'isbn': None,
                    'work_id': None,
                    'openlibrary_key': None,
                    'openlibrary_url': None,
                    'work_url': None
                }
                return title, book_info
                
        except Exception as e:
            print(f"Error processing book '{title}' by '{author}': {e}")
            return title, None
    
    def process_unique_books(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Process unique books from DataFrame using concurrent requests.
        
        Args:
            df: DataFrame with book data
            
        Returns:
            Dict mapping book titles to enhanced information
        """
        unique_titles = df['Title'].unique()
        title_to_info = {}
        books_with_no_info = []
        
        print(f"Processing {len(unique_titles)} unique books with {self.max_workers} concurrent workers...")
        
        # Create list of (title, author) tuples for processing
        book_tasks = []
        for title in unique_titles:
            if title != "Unknown":
                author_row = df[df['Title'] == title]['Author'].iloc[0] if len(df[df['Title'] == title]) > 0 else "Unknown"
                book_tasks.append((title, author_row))
        
        # Process books concurrently
        completed_count = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_book = {
                executor.submit(self.process_single_book, title, author): (title, author)
                for title, author in book_tasks
            }
            
            # Process completed tasks
            for future in as_completed(future_to_book):
                title, author = future_to_book[future]
                completed_count += 1
                
                try:
                    result_title, book_info = future.result()
                    
                    if book_info:
                        title_to_info[result_title] = book_info
                        themes_str = ', '.join(book_info['themes']) if book_info['themes'] else 'None'
                        print(f"  ✅ ({completed_count}/{len(book_tasks)}) {result_title}: {themes_str}")
                    else:
                        books_with_no_info.append({
                            'Title': title,
                            'Author': author,
                            'Status': 'No info or themes found'
                        })
                        print(f"  ❌ ({completed_count}/{len(book_tasks)}) {title}: No info found")
                    
                    # Print progress every 50 books
                    if completed_count % 50 == 0:
                        print(f"  💾 Progress: {completed_count}/{len(book_tasks)} books processed...")
                        
                except Exception as e:
                    print(f"  💥 Error processing {title}: {e}")
        
        # Save books with no info
        if books_with_no_info:
            no_info_df = pd.DataFrame(books_with_no_info)
            no_info_df.to_csv("books_no_info_found.csv", index=False)
            print(f"Saved {len(books_with_no_info)} books with no info to books_no_info_found.csv")
        
        return title_to_info
    
    def enhance_multiple_csv_files(self, csv_files: list, output_file: str):
        """
        Main method to enhance multiple CSV files with book information and themes.
        
        Args:
            csv_files: List of paths to input CSV files
            output_file: Path to output enhanced CSV file
        """
        print(f"Loading CSV data from {len(csv_files)} files...")
        
        # Load and combine CSV data
        dataframes = []
        for csv_file in csv_files:
            print(f"  Loading {csv_file}...")
            df = pd.read_csv(csv_file)
            dataframes.append(df)
        
        # Combine all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)
        print(f"Combined {len(combined_df)} total records from all CSV files")
        
        # Clean the combined data
        combined_df = combined_df.fillna({
            "Title": "Unknown",
            "Author": "Unknown",
            "State": "Unknown",
            "District": "Unknown",
            "Date of Challenge/Removal": "Unknown",
            "Ban Status": "Unknown",
        })
        
        # Process unique books
        title_to_info = self.process_unique_books(combined_df)
        
        # Add new columns to dataframe
        new_columns = ['description', 'themes', 'cover_url', 'publish_year', 'isbn', 'work_id', 'openlibrary_url', 'work_url']
        for col in new_columns:
            combined_df[col] = ""
        
        # Apply book info to dataframe
        for index, row in combined_df.iterrows():
            title = row['Title']
            book_info = title_to_info.get(title)
            
            if book_info:
                combined_df.at[index, 'description'] = book_info['description'] or ""
                combined_df.at[index, 'themes'] = ', '.join(book_info['themes']) if book_info['themes'] else ""
                combined_df.at[index, 'cover_url'] = book_info['cover_url'] or ""
                combined_df.at[index, 'publish_year'] = book_info['publish_year'] or ""
                combined_df.at[index, 'isbn'] = book_info['isbn'] or ""
                combined_df.at[index, 'work_id'] = book_info['work_id'] or ""
                combined_df.at[index, 'openlibrary_url'] = book_info['openlibrary_url'] or ""
                combined_df.at[index, 'work_url'] = book_info['work_url'] or ""
        
        # Save enhanced data
        print(f"Saving enhanced data to {output_file}...")
        combined_df.to_csv(output_file, index=False)
        
        # Print statistics
        books_with_themes = combined_df[combined_df['themes'].str.len() > 0]['Title'].nunique()
        books_with_descriptions = combined_df[combined_df['description'].str.contains("No description available", na=False) == False]['Title'].nunique()
        total_unique_books = combined_df['Title'].nunique()
        
        print(f"\n📊 Enhancement Summary:")
        print(f"Total records processed: {len(combined_df)}")
        print(f"Total unique books: {total_unique_books}")
        print(f"Books with themes: {books_with_themes} ({(books_with_themes/total_unique_books)*100:.1f}%)")
        print(f"Books with descriptions: {books_with_descriptions} ({(books_with_descriptions/total_unique_books)*100:.1f}%)")
        print("✅ Enhancement complete!")

if __name__ == "__main__":
    # Create enhancer with 10 concurrent workers and 5 requests per second
    enhancer = BookInfoEnhancer(max_workers=10, requests_per_second=5)
    
    # Process both CSV files
    csv_files = [
        "/Users/dana/code/book-bans/PenAmericaData/PEN America's Index of School Book Bans (July 1, 2022 - June 30, 2023) - Sorted by Author & Title.csv",
        "/Users/dana/code/book-bans/PenAmericaData/Pen America's Index of School Books Bans 2024 2025.csv"
    ]
    
    enhancer.enhance_multiple_csv_files(
        csv_files,
        "enhanced_book_bans_combined.csv"
    )
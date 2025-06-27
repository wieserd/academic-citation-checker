import re

def parse_source_list(source_file_path):
    """Parses the user-provided list of sources."""
    user_sources = set()
    try:
        with open(source_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Regex to find Author, A. A. (YYYY) or Author, A. A., & Another, B. B. (YYYY)
                # This regex is more flexible for full bibliography entries.
                # Refined regex to capture author and year from the beginning of the line
                # It looks for an author name (can include initials) followed by a year.
                # It tries to be robust to common variations in citation formats.
                match = re.search(r'^\s*([A-Za-zÀ-ÖØ-öø-ÿ]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ]\.?)*)(?:\s+et\s+al\.)?[^\d]*((?:19|20)\d{2})', line)
                if match:
                    author_part = match.group(1).split(',')[0].strip() # Get the first author's last name
                    year = match.group(2)
                    standardized_source = f"{author_part.lower()}_{year}"
                    user_sources.add(standardized_source)
                    
    except FileNotFoundError:
        print(f"Error: The source list file at {source_file_path} was not found.")
        return set()
    except Exception as e:
        print(f"An error occurred while reading the source list: {e}")
        return set()
    
    return list(user_sources)

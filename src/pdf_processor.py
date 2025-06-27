import re
import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file, returning a list of page texts."""
    pages_text = []
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                pages_text.append(page.extract_text() or "")
    except FileNotFoundError:
        print(f"Error: The file at {pdf_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return None
    return pages_text

def extract_bibliography_text(pages_text, last_n_pages=20):
    """Attempts to extract the bibliography section from the last N pages of the PDF."""
    combined_text = ""
    start_page_index = max(0, len(pages_text) - last_n_pages)
    for i in range(start_page_index, len(pages_text)):
        combined_text += pages_text[i]

    # Common headers for bibliography sections
    bibliography_headers = [
        "References",
        "Bibliography",
        "Literature Cited",
        "Works Cited",
        "Publications"
    ]

    # Create a regex pattern to find any of these headers, case-insensitive
    pattern = r"\b(?:" + "|".join(bibliography_headers) + r")\b"
    match = re.search(pattern, combined_text, re.IGNORECASE)

    if match:
        # Return text from the start of the matched header to the end of the combined text
        return combined_text[match.start():]
    else:
        return ""

def fix_hyphenated_words(text):
    """Joins lines and fixes hyphenated words split across lines, and removes PDF artifacts."""
    # Fix words split by hyphen and newline/space (e.g., "Com- plex" or "Com-\nplex")
    fixed_text = re.sub(r'([a-zA-Z]+)-\s*\n?\s*([a-zA-Z]+)', r'\1\2', text)
    # Remove PDF artifacts like /f_ or /T_
    fixed_text = re.sub(r'/[a-zA-Z]_|\[\d+\]', '', fixed_text) # Also remove [numbers] that might be left from IEEE
    return fixed_text


def parse_bibliography_entries(bibliography_text):
    """Parses the bibliography text into individual entries and extracts primary author for sorting."""
    entries = []
    lines = bibliography_text.splitlines()

    current_entry_lines = []
    current_author_for_sort = ""
    prev_indent = 0

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped: # Skip empty lines
            continue

        current_indent = len(line) - len(line.lstrip())

        # Heuristic: A new entry typically starts with less or equal indentation than the previous line
        # or if it's the very first line.
        is_new_entry_start = False
        if i == 0: # First line is always a potential start
            is_new_entry_start = True
        elif current_indent <= prev_indent: # New entry if indentation is less or equal
            is_new_entry_start = True
        elif current_indent > prev_indent and not current_entry_lines: # If indented but no current entry, it's a new start
            is_new_entry_start = True

        if is_new_entry_start:
            # Process the previous entry before starting a new one
            if current_entry_lines:
                processed_entry_text = fix_hyphenated_words(" ".join(current_entry_lines))
                # Attempt to extract author for sorting from the processed entry
                author_match = re.search(r'^\s*(?:\d+\.\s*)?([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+)*)', processed_entry_text)
                if author_match:
                    current_author_for_sort = author_match.group(1).split(',')[0].strip().lower()
                    entries.append((processed_entry_text, current_author_for_sort))
                else:
                    # If no author found, it might not be a valid entry, or we can use a placeholder
                    entries.append((processed_entry_text, "zz_no_author")) # Sort non-matching to end

            # Start new entry
            current_entry_lines = [line_stripped]
        else:
            # Continuation of the current entry
            current_entry_lines.append(line_stripped)

        prev_indent = current_indent

    # Process the last entry after the loop finishes
    if current_entry_lines:
        processed_entry_text = fix_hyphenated_words(" ".join(current_entry_lines))
        author_match = re.search(r'^\s*(?:\d+\.\s*)?([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+)*)', processed_entry_text)
        if author_match:
            current_author_for_sort = author_match.group(1).split(',')[0].strip().lower()
            entries.append((processed_entry_text, current_author_for_sort))
        else:
            entries.append((processed_entry_text, "zz_no_author"))

    # Filter out entries that are too short or clearly not bibliographic
    # This is a heuristic and might need adjustment.
    filtered_entries = []
    for entry_text, sort_key in entries:
        # Heuristic: entries should be at least 20 characters long and not just a URL or single word
        if len(entry_text) > 20 and not entry_text.startswith("http") and " " in entry_text:
            filtered_entries.append((entry_text, sort_key))

    # Sort entries by the extracted author's last name
    filtered_entries.sort(key=lambda x: x[1])

    return [entry_text for entry_text, _ in filtered_entries]

def find_citations_in_text(pages_text):
    """Finds citations in the extracted text, including page numbers."""
    author_year_regex = re.compile(r'''
        (?P<author>[A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+)*) # Author(s)
        (?:\s+et\s+al\.? )?                                  # Optional "et al."
        (?:                                                    # Group for year part (either parenthesized or not)
            \s*\(                                            # Option 1: Parenthesized year
            (?P<year_paren>(?:19|20)\d{2})                    # Year inside parentheses
            (?:,\s*(?:p\.?|pp\.?)\s*\d+(?:-\d+)?)?       # Optional page numbers
            \)                                                # Close parenthesis for parenthesized year
        |
            (?:,\s*|\s+)                                     # Option 2: Non-parenthesized year
            (?P<year_noparen>(?:19|20)\d{2})                  # Year without parentheses
            (?:,\s*(?:p\.?|pp\.?)\s*\d+(?:-\d+)?)?       # Optional page numbers
        )
    ''', re.VERBOSE)

    # Regex for IEEE-style numerical citations: [1], [2,3], [4]-[6]
    ieee_regex = re.compile(r'\[(?:\d+(?:,\s*\d+)*|\d+-\d+)\]')

    found_author_year_citations = set()
    found_ieee_citations = set()

    for page_num, page_text in enumerate(pages_text, 1):
        # Find author-year citations
        for match in author_year_regex.finditer(page_text):
            author = match.group('author')
            year = match.group('year_paren') or match.group('year_noparen')
            if author and year:
                standardized_citation = f"{author.lower()}_{year}"
                found_author_year_citations.add((standardized_citation, page_num))

        # Find IEEE-style citations
        for match in ieee_regex.finditer(page_text):
            ieee_citation_text = match.group(0)
            found_ieee_citations.add((ieee_citation_text, page_num))

    return list(found_author_year_citations), list(found_ieee_citations)
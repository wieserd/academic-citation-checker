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

def fix_hyphenated_words(lines):
    """Joins lines and fixes hyphenated words split across lines."""
    joined_text = " ".join(lines)
    # Regex to find a word ending with a hyphen, followed by a space and a word starting with a letter
    # and replace it with the two words joined without the hyphen and space.
    # Example: "Com- plex" -> "Complex"
    fixed_text = re.sub(r'([a-zA-Z]+)-\s+([a-zA-Z]+)', r'\1\2', joined_text)
    return fixed_text

def parse_bibliography_entries(bibliography_text):
    """Parses the bibliography text into individual entries and extracts primary author for sorting."""
    entries = []
    # This regex attempts to find lines starting with a capital letter (likely an author's last name)
    # or a number (for numbered lists), followed by content, and then captures the first word
    # that looks like a last name for sorting.
    # It's a heuristic and might need adjustment for specific bibliography styles.
    entry_start_pattern = re.compile(r'^\s*(?:\d+\.\s*)?([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+)*).*$', re.MULTILINE)

    current_entry_lines = []
    current_author_for_sort = ""

    for line in bibliography_text.splitlines():
        line_stripped = line.strip()
        if not line_stripped: # Skip empty lines
            continue

        match = entry_start_pattern.match(line_stripped)
        if match:
            # New entry starts
            if current_entry_lines:
                # Process the previous entry before starting a new one
                processed_entry_text = fix_hyphenated_words(current_entry_lines)
                entries.append((processed_entry_text, current_author_for_sort))

            # Start new entry
            # Remove leading numbering if present
            line_without_number = re.sub(r'^\s*\d+\.\s*', '', line_stripped)
            current_entry_lines = [line_without_number]
            current_author_for_sort = match.group(1).split(',')[0].strip().lower()
        else:
            # Continuation of the current entry
            if current_entry_lines:
                current_entry_lines.append(line_stripped)

    # Add the last entry after the loop finishes
    if current_entry_lines:
        processed_entry_text = fix_hyphenated_words(current_entry_lines)
        entries.append((processed_entry_text, current_author_for_sort))

    # Sort entries by the extracted author's last name
    entries.sort(key=lambda x: x[1])

    return [entry_text for entry_text, _ in entries]

def find_citations_in_text(pages_text):
    """Finds citations in the extracted text, including page numbers."""
    author_year_regex = re.compile(r'''
        (?P<author>[A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+)*) # Author(s)
        (?:\s+et\s+al\.?)?                                  # Optional "et al."
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

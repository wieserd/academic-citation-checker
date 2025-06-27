import re
import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
    except FileNotFoundError:
        print(f"Error: The file at {pdf_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return None
    return text





def find_citations_in_text(text):
    """Finds citations in the extracted text."""
    # Regex to find patterns like (Author, YYYY) or (Author et al., YYYY)
    # This is a simplified regex and might need to be adjusted for different citation styles.
    citation_regex = re.compile(r'''
        (?P<author>[A-Z][a-zA-Z'-]+)         # Author's last name
        (?:\s+et\s+al\.?|)?                  # Optional "et al."
        \s*\(                             # Opening parenthesis for year
        (?P<year>(?:19|20)\d{2})             # Year (19xx or 20xx)
        \)                                  # Closing parenthesis
        (?!\.)                               # Negative lookahead: ensure no period immediately follows
    ''', re.VERBOSE)

    found_citations = set()
    for match in citation_regex.finditer(text):
        author = match.group('author')
        year = match.group('year')
        # Standardize the citation format for comparison
        found_citations.add(f"{author.lower()}_{year}")

    return list(found_citations)

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

def compare_sources(pdf_citations, user_sources):
    """Compares the found citations with the user's source list."""
    found_sources = []
    not_found_sources = []
    pdf_only_citations = []

    # Convert user_sources to a set for faster lookup
    user_sources_set = set(user_sources)

    for pdf_citation in pdf_citations:
        if pdf_citation not in user_sources_set:
            pdf_only_citations.append(pdf_citation)

    for user_source in user_sources:
        if user_source in set(pdf_citations):
            found_sources.append(user_source)
        else:
            not_found_sources.append(user_source)

    return found_sources, not_found_sources, pdf_only_citations

def main():
    """Main function to run the application."""
    pdf_path = input("Enter the path to your PDF file: ")
    source_file_path = input("Enter the path to your source list file: ")

    pdf_text = extract_text_from_pdf(pdf_path)
    if pdf_text is None:
        return # Exit if PDF text extraction failed

    pdf_citations = find_citations_in_text(pdf_text)
    user_sources = parse_source_list(source_file_path)
    found_sources, not_found_sources, pdf_only_citations = compare_sources(pdf_citations, user_sources)

    print("\n--- Results ---")
    

    print(f"\n--- Citations exist in both ({len(found_sources)} found) ---")
    print("These are the entries from your provided source list for which a corresponding citation (based on author's last name and year) was found within the PDF document.")
    if found_sources:
        for source in found_sources:
            print(f"- {source}")
    else:
        print("No entry")

    print(f"\n--- List only ({len(not_found_sources)} found) ---")
    print("These are the entries from your provided source list for which no corresponding citation (based on author's last name and year) was found within the PDF document.")
    if not_found_sources:
        for source in not_found_sources:
            print(f"- {source}")
    else:
        print("No entry")

    print("\n")
    print(f"--- PDF only ({len(pdf_only_citations)} found) ---")
    print("These are citations found in the PDF document that do not have a corresponding entry in your provided source list.")
    if pdf_only_citations:
        for citation in pdf_only_citations:
            print(f"- {citation}")
    else:
        print("No entry")

if __name__ == "__main__":
    main()

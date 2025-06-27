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

def find_citations_in_text(pages_text):
    """Finds citations in the extracted text, including page numbers."""
    author_year_regex = re.compile(r'''
        (?P<author>[A-Z][a-zA-Z'\-]+(?:\s+[A-Z][a-zA-Z'\-]+)*) # Author(s)
        (?:\s+et\s+al\.?)?                                  # Optional "et al."
        (?:                                                    # Non-capturing group for the year part
            \s*\(                                            # Parenthesized year
            (?P<year_in_paren>(?:19|20)\d{2})                 # Year inside parentheses
            (?:,\s*(?:p\.?|pp\.?)\s*\d+(?:-\d+)?)?       # Optional page numbers
            \)
        |
            (?:,\s*|\s+)                                     # Comma or space separated year
            (?P<year_no_paren>(?:19|20)\d{2})                 # Year without parentheses
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
            year = match.group('year_in_paren') or match.group('year_no_paren')
            if author and year:
                standardized_citation = f"{author.lower()}_{year}"
                found_author_year_citations.add((standardized_citation, page_num))

        # Find IEEE-style citations
        for match in ieee_regex.finditer(page_text):
            ieee_citation_text = match.group(0)
            found_ieee_citations.add((ieee_citation_text, page_num))

    return list(found_author_year_citations), list(found_ieee_citations)

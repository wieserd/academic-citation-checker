import os
import time
from pdf_processor import extract_text_from_pdf, find_citations_in_text, extract_bibliography_text, parse_bibliography_entries
from source_parser import parse_source_list
from comparator import compare_sources

def animate_message(message, duration=1):
    end_time = time.time() + duration
    while time.time() < end_time:
        for char in ['|', '/', '-', '\\']:
            print(f"\r{message} {char}", end='', flush=True)
            time.sleep(0.1)
    print(f"\r{message}   ", flush=True) # Clear animation characters

def main():
    """Main function to run the application."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    paths_file = os.path.join(project_root, "data", "paths.txt")

    # Ensure the data directory exists
    data_dir = os.path.dirname(paths_file)
    os.makedirs(data_dir, exist_ok=True)
    pdf_path = None
    source_file_path = None

    # Try to read paths from file
    try:
        with open(paths_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                pdf_path = lines[0].strip()
                source_file_path = lines[1].strip()
                animate_message("Reading paths from paths.txt", duration=1)
                print("Reading paths from paths.txt ... SUCCESS!!")
            else:
                print(f"{paths_file} found but does not contain both paths. Prompting user.")
    except FileNotFoundError:
        print(f"{paths_file} not found. Prompting user for paths.")
    except Exception as e:
        print(f"An error occurred while reading {paths_file}: {e}. Prompting user.")

    # If paths not found in file, prompt user
    if pdf_path is None or source_file_path is None:
        pdf_path = input("Enter the absolute path to your PDF file: ")
        source_file_path = input("Enter the absolute path to your source list file: ")

        # Save paths to file for future use
        try:
            with open(paths_file, 'w') as f:
                f.write(f"{pdf_path}\n")
                f.write(f"{source_file_path}\n")
            print(f"Paths saved to {paths_file} for future use.")
        except Exception as e:
            print(f"Error saving paths to {paths_file}: {e}")

    pdf_text_pages = extract_text_from_pdf(pdf_path)
    if pdf_text_pages is None:
        return # Exit if PDF text extraction failed

    pdf_citations = []
    ieee_citations = []
    if pdf_text_pages: # Only call find_citations_in_text if there's text to process
        pdf_citations, ieee_citations = find_citations_in_text(pdf_text_pages)

    user_sources = parse_source_list(source_file_path)
    found_sources, not_found_sources, pdf_only_citations = compare_sources(pdf_citations, user_sources)

    # Get all page numbers from the PDF
    all_pages = set(range(1, len(pdf_text_pages) + 1))

    # Get all pages where citations were found (from both author-year and IEEE)
    cited_pages = set()
    for _, page_num in pdf_citations:
        cited_pages.add(page_num)
    for _, page_num in ieee_citations:
        cited_pages.add(page_num)

    # Determine pages without citations
    uncited_pages = sorted(list(all_pages - cited_pages))

    # Group consecutive uncited pages
    grouped_uncited_pages = []
    if uncited_pages:
        start = uncited_pages[0]
        end = uncited_pages[0]
        for i in range(1, len(uncited_pages)):
            if uncited_pages[i] == end + 1:
                end = uncited_pages[i]
            else:
                if end - start >= 3:
                    grouped_uncited_pages.append(f"pages {start}-{end}")
                elif start == end:
                    grouped_uncited_pages.append(f"page {start}")
                else:
                    grouped_uncited_pages.append(f"pages {start}, {end}")
                start = uncited_pages[i]
                end = uncited_pages[i]
        # Add the last group
        if end - start >= 3:
            grouped_uncited_pages.append(f"pages {start}-{end}")
        elif start == end:
            grouped_uncited_pages.append(f"page {start}")
        else:
            grouped_uncited_pages.append(f"pages {start}, {end}")

    # Sort the lists for consistent output
    found_sources.sort(key=lambda x: x[1][0] if x[1] else '') # Sort by first page number
    not_found_sources.sort() # Sort by citation string
    pdf_only_citations.sort(key=lambda x: x[1][0] if x[1] else '') # Sort by first page number

    # Sort IEEE citations by page number
    ieee_citations.sort(key=lambda x: x[1])

    output_content = []

    output_content.append("\n--- Results ---")

    output_content.append(f"\n--- Citations exist in both ({len(found_sources)} found) ---")
    output_content.append("These are the entries from your provided source list for which a corresponding citation (based on author's last name and year) was found within the PDF document.")
    if found_sources:
        for source, pages in found_sources:
            output_content.append(f"- [pages {', '.join(map(str, pages))}] {source}")
    else:
        output_content.append("No entry")

    output_content.append(f"\n--- List only ({len(not_found_sources)} found) ---")
    output_content.append("These are the entries from your provided source list for which no corresponding citation (based on author's last name and year) was found within the PDF document.")
    if not_found_sources:
        for source in not_found_sources:
            output_content.append(f"- {source}")
    else:
        output_content.append("No entry")

    output_content.append("\n")
    output_content.append(f"--- PDF only ({len(pdf_only_citations)} found) ---")
    output_content.append("These are citations found in the PDF document that do not have a corresponding entry in your provided source list.")
    if pdf_only_citations:
        for citation, pages in pdf_only_citations:
            output_content.append(f"- [pages {', '.join(map(str, pages))}] {citation}")
    else:
        output_content.append("No entry")

    output_content.append(f"\n--- Citation-Free Pages ({len(grouped_uncited_pages)} groups) ---")
    output_content.append("These are pages in the PDF where no citations were found.")
    if grouped_uncited_pages:
        for page_group in grouped_uncited_pages:
            output_content.append(f"- {page_group}")
    else:
        output_content.append("No entry")

    output_content.append(f"\n--- IEEE-style Citations Found ({len(ieee_citations)} found) ---")
    output_content.append("These are numerical citations found in the PDF, typically used in IEEE style.")
    if ieee_citations:
        # Group IEEE citations by page for cleaner output
        ieee_citations_by_page = {}
        for citation_text, page_num in ieee_citations:
            if page_num not in ieee_citations_by_page:
                ieee_citations_by_page[page_num] = []
            ieee_citations_by_page[page_num].append(citation_text)

        for page_num in sorted(ieee_citations_by_page.keys()):
            citations_on_page = ', '.join(sorted(list(set(ieee_citations_by_page[page_num]))))
            output_content.append(f"- [page {page_num}] {citations_on_page}")
    else:
        output_content.append("No entry")

    # Write output to file
    result_file_path = os.path.join(project_root, "data", "result.txt")
    try:
        with open(result_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_content))
        print(f"\nResults saved to {result_file_path}")
    except Exception as e:
        print(f"Error saving results to {result_file_path}: {e}")

    # Also print to console for immediate feedback
    print("\n".join(output_content))

    # Optional bibliography extraction
    extract_bib = input("\nWe could also extract the bibliography from the PDF. Would you like that? (yes/no): ").lower()
    if extract_bib == 'yes':
        pdf_bibliography_entries = []
        if pdf_text_pages:
            bibliography_text = extract_bibliography_text(pdf_text_pages)
            if bibliography_text:
                pdf_bibliography_entries = parse_bibliography_entries(bibliography_text)

        bib_output_content = []
        bib_output_content.append(f"\n--- Extracted Bibliography from PDF ({len(pdf_bibliography_entries)} entries) ---")
        bib_output_content.append("These are entries extracted from the bibliography/references section of the PDF, sorted by primary author.")
        if pdf_bibliography_entries:
            for entry in pdf_bibliography_entries:
                bib_output_content.append(f"- {entry}")
        else:
            bib_output_content.append("No entry")

        # Append bibliography output to result.txt and print to console
        try:
            with open(result_file_path, 'a', encoding='utf-8') as f:
                f.write("\n".join(bib_output_content))
            print(f"\nBibliography appended to {result_file_path}")
        except Exception as e:
            print(f"Error appending bibliography to {result_file_path}: {e}")

        print("\n".join(bib_output_content))

if __name__ == "__main__":
    main()

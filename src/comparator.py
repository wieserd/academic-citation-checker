def compare_sources(pdf_citations_with_pages, user_sources):
    """Compares the found citations with the user's source list, including page numbers."""
    found_sources = []
    not_found_sources = []
    pdf_only_citations = []

    # Create a set of just the citation strings from the PDF for quick lookup
    pdf_citation_strings = {citation for citation, page in pdf_citations_with_pages}

    # Convert user_sources to a set for faster lookup
    user_sources_set = set(user_sources)

    # Identify PDF-only citations
    pdf_only_citations_map = {}
    for citation, page in pdf_citations_with_pages:
        if citation not in user_sources_set:
            if citation not in pdf_only_citations_map:
                pdf_only_citations_map[citation] = set()
            pdf_only_citations_map[citation].add(page)

    pdf_only_citations = []
    for citation, pages in pdf_only_citations_map.items():
        pdf_only_citations.append((citation, sorted(list(pages))))

    # Identify matched and unmatched user sources
    for user_source in user_sources:
        if user_source in pdf_citation_strings:
            # Find all pages where this user_source is cited in the PDF
            pages_for_source = sorted(list(set([page for citation, page in pdf_citations_with_pages if citation == user_source])))
            found_sources.append((user_source, pages_for_source))
        else:
            not_found_sources.append(user_source)

    return found_sources, not_found_sources, pdf_only_citations

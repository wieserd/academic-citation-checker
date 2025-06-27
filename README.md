# PDF Citation Checker

This is a command-line application designed to help academic researchers and writers compare citations found within a PDF document against a personal list of sources.

## Features

*   **Extracts In-Text Citations:** Scans PDF documents for common in-text citation patterns (e.g., "Author (YYYY)").
*   **Compares with User-Provided List:** Takes a text file containing your full bibliography and extracts author-year pairs for comparison.
*   **Categorized Output:** Provides a clear breakdown of:
    *   Citations found in both the PDF and your source list.
    *   Sources from your list that are *not* found in the PDF.
    *   Citations found in the PDF that are *not* in your source list.
    *   Pages in the PDF where no citations were found.
    *   IEEE-style numerical citations found in the PDF.

## How It Works

The application processes your PDF and source list, standardizing citations to a "lastname_year" format (e.g., "porter_2001") for effective comparison.

## Project Structure

```
pdf_source_checker/
├── src/
│   ├── main.py
│   ├── pdf_processor.py
│   ├── source_parser.py
│   ├── comparator.py
│   └── requirements.txt
├── data/
│   ├── book.pdf
│   ├── source_list.txt
│   ├── paths.txt
│   └── result.txt
└── README.md
```

## Installation

1.  **Navigate to the `src` directory:**
    ```bash
    cd /Users/YOUR_USERNAME/pdf_source_checker/src
    ```
2.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    From the `src` directory in your terminal, execute the main script:
    ```bash
    python main.py
    ```

## Output Explanation

The application will output several distinct sections, both to the console and saved to `data/result.txt`:

*   **--- Citations exist in both (X found) ---**
    These are the entries from your provided source list for which a corresponding citation (based on author's last name and year) was found within the PDF document. These are sorted by their lowest page number. If no entries are found, it will display "No entry".

*   **--- List only (Y found) ---**
    These are the entries from your provided source list for which no corresponding citation (based on author's last name and year) was found within the PDF document. This indicates sources you have, but are not cited in the PDF. These are sorted alphabetically by citation string. If no entries are found, it will display "No entry".

*   **--- PDF only (Z found) ---**
    These are citations found in the PDF document that do not have a corresponding entry in your provided source list. This can help you identify sources cited in the PDF that you might not have in your personal bibliography. These are sorted by their lowest page number. If no entries are found, it will display "No entry".

*   **--- Citation-Free Pages (A groups) ---**
    These are pages in the PDF where no citations (author-year or IEEE-style) were found. Consecutive pages are grouped into ranges (e.g., "pages 40-45" for 3 or more consecutive pages, "page 10" for single pages, or "pages 12, 13" for two consecutive pages). If no such pages are found, it will display "No entry".

*   **--- IEEE-style Citations Found (B found) ---**
    These are numerical citations found in the PDF (e.g., `[1]`, `[2,3]`, `[4]-[6]`), typically used in IEEE style. They are grouped by page number. If no entries are found, it will display "No entry".

## Current Limitations / Assumptions

*   **In-text Citation Detection:** The application now uses a more flexible regular expression to detect a wider variety of in-text citation patterns, including those with and without parentheses, "et al.", and optional page numbers (e.g., "Author (YYYY)", "Author, YYYY", "Author et al. (YYYY, p. X)"). It also specifically identifies IEEE-style numerical citations (e.g., `[1]`, `[2,3]`).
*   **Source List Parsing:** The `parse_source_list` function uses a regular expression to extract the first author's last name and the year from the beginning of each line in your source file. It expects a format where the author's last name and a four-digit year (19xx or 20xx) are present and relatively early in the line. Unusual or highly varied bibliographic formats might not be parsed correctly.

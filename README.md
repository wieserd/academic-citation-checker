# PDF Citation Checker

This is a command-line application designed to help academic researchers and writers compare citations found within a PDF document against a personal list of sources.

## Features

*   **Extracts In-Text Citations:** Scans PDF documents for common in-text citation patterns (e.g., "Author (YYYY)").
*   **Compares with User-Provided List:** Takes a text file containing your full bibliography and extracts author-year pairs for comparison.
*   **Categorized Output:** Provides a clear breakdown of:
    *   Citations found in both the PDF and your source list.
    *   Sources from your list that are *not* found in the PDF.
    *   Citations found in the PDF that are *not* in your source list.

## How It Works

The application processes your PDF and source list, standardizing citations to a "lastname_year" format (e.g., "porter_2001") for effective comparison.

## Installation

1.  **Navigate to the project directory:**
    ```bash
    cd /pdf_source_checker
    ```
2.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Prepare your source list file:**
    Create a plain text file (e.g., `my_sources.txt`) where each line contains one full bibliographic entry from your list of sources. The application will attempt to extract the primary author's last name and the publication year from each line.

    **Example `my_sources.txt` content:**
    ```
    Clark, E., Brenson, F., & Johnson, P. (1999). The ultimate title: A study of academic citations. Journal of Citation Studies, 1(1), 1-10.
    Wieser, D. (2023). My research paper on citation analysis. Unpublished manuscript.
    Porter, M. A. (2001). An Introduction to Quantum Chaos (Version 2). arXiv. https://doi.org/10.48550/ARXIV.NLIN/0107039
    ```

2.  **Run the application:**
    From the project directory in your terminal, execute the main script:
    ```bash
    python main.py
    ```

3.  **Follow the prompts:**
    The application will ask you to enter the absolute path to your PDF file and the absolute path to your source list file.

## Output Explanation

The application will output three distinct sections:

*   **--- Citations exist in both (X found) ---**
    These are the entries from your provided source list for which a corresponding citation (based on author's last name and year) was found within the PDF document. If no entries are found, it will display "No entry".

*   **--- List only (Y found) ---**
    These are the entries from your provided source list for which no corresponding citation (based on author's last name and year) was found within the PDF document. This indicates sources you have, but are not cited in the PDF. If no entries are found, it will display "No entry".

*   **--- PDF only (Z found) ---**
    These are citations found in the PDF document that do not have a corresponding entry in your provided source list. This can help you identify sources cited in the PDF that you might not have in your personal bibliography. If no entries are found, it will display "No entry".

## Current Limitations / Assumptions

*   **In-text Citation Format:** The application primarily looks for citations in the format "Author (YYYY)" (e.g., "Porter (2001)") and specifically excludes those immediately followed by a period, assuming these are footnote-style citations without additional text.
*   **Source List Parsing:** The `parse_source_list` function uses a regular expression to extract the first author's last name and the year from the beginning of each line in your source file. It expects a format where the author's last name and a four-digit year (19xx or 20xx) are present and relatively early in the line. Unusual or highly varied bibliographic formats might not be parsed correctly.

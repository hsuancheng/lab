---
name: import_publications_from_latex
description: Parse a LaTeX publication list into JSON and render it in an Astro web application, handling custom formatting, grouping, and sorting.
---

# Import Publications from LaTeX

This skill guides the process of converting a raw LaTeX bibliography file (using custom macros) into a structured JSON dataset and displaying it on an Astro-based website.

## Prerequisites

- A Python environment to run the parsing script.
- An Astro project with a `src/content` directory.
- A source LaTeX file (e.g., `pub-YYMMDD.tex`) containing publication items.

## Step-by-Step Workflow

1. **Configure the Parser Script**
    - Locate or create `scripts/parse_latex_publications.py`.
    - Update the `latex_file` variable in the `__main__` block to point to the new source LaTeX file (e.g., `pub-260201.tex`).
    - Ensure the script handles custom LaTeX macros commonly used in the lab's file:
        - `\mypub{Title}{Authors}{Venue}`
        - `\mybpub{Title}{Authors}{Venue}` (Bold title)
        - `\newpub{Authors}{Title}{Venue}` (Note: Swapped arguments)
        - `{\bf Books \& Chapters:}` section marker.

2. **Execute Parsing**
    - Run the script: `python3 scripts/parse_latex_publications.py`.
    - This generates `src/content/publications.json`.
    - **Validation**:
        - Check total count against expected numbers.
        - Verify special symbols (e.g., replace `\dagger` or `$^\dagger$` with `†`).
        - Verify that "Books & Chapters" are correctly tagged with `"type": "book"`.
        - Verify that "Journal Papers" are tagged with `"type": "journal"` (default).

3. **Update Frontend Rendering (`PublicationsList.astro`)**
    - Read `src/content/publications.json`.
    - **Filtering**: Separate items into `journals` and `books` based on the `type` field.
    - **Sorting**:
        - **Journals**: Apply hybrid sorting if requested.
            - *Head*: Keep the original LaTeX order for the first N items (e.g., 20) to respect "selected" or "highlighted" ordering.
            - *Tail*: Sort the remaining items by `year` (descending).
        - **Books**: Usually displayed as a flat list, preserving LaTeX order.
    - **Grouping**: Group journals by Year for display, but ensure continuous numbering across groups.
    - **Formatting**: Remove DOI links if requested. Ensure authors, title, and venue are styled correctly.

4. **Verification**
    - Run `npm run build` to ensure the Astro content schema is valid and the site builds.
    - Commit changes: `git add . && git commit -m "Update publications from [filename]"`.

## Inputs & Outputs

- **Inputs**:
  - Source LaTeX file (absolute path).
  - Natural language instructions for sorting (e.g., "Keep top 20 fixed").
- **Outputs**:
  - `src/content/publications.json`: The structured data.
  - `src/components/PublicationsList.astro`: The rendering logic.
  - Pass/Fail status of `npm run build`.

## Best Practices & Constraints

- **Parser Logic**:
  - Use Regex for parsing LaTeX instead of strict TeX parsers to handle non-standard macros gracefully.
  - Always strip LaTeX comments (`%`) before processing to avoid counting commented-out papers.
  - Clean LaTeX artifacts (braces `{}`, styles `\bf`, `\it`) during extraction.
- **Code Style**:
  - Use Python for data processing scripts.
  - Use Astro/JSX for the frontend component.
- **Data Structure**:
  - Maintain a flat JSON array in `publications.json` with a added `type` field for categorization, rather than creating nesting or separate layout files. This keeps the schema simple.

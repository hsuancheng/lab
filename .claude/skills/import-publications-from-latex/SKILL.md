---
name: import-publications-from-latex
description: Update the lab site's publication list from a new LaTeX source file (pub-YYMMDD.tex). Parses the LaTeX into publications.json and adjusts rendering in PublicationsList.astro. Use when HC provides a new pub-*.tex file or asks to update/re-sort publications.
---

# Import Publications from LaTeX

Convert a raw LaTeX bibliography file (using custom macros) into a structured JSON dataset and display it on the Astro site.

## Prerequisites

- Python available (the parser is stdlib-only, so `python3` works; the project also has `.venv/`).
- The canonical source at `sources/pub.tex`.

## Step-by-Step Workflow

1. **Install the New Source**
    - HC sends dated files (e.g., `pub-20260802.tex`). Copy the new file over `sources/pub.tex` —
      do **not** add a dated file to the repo. Git history is the archive and the parser path stays fixed.
    - Confirm the macros the script handles are still the ones in use:
        - `\mypub{Title}{Authors}{Venue}`
        - `\mybpub{Title}{Authors}{Venue}` (Bold title)
        - `\newpub{Authors}{Title}{Venue}` (Note: swapped arguments)
        - `{\bf Books \& Chapters:}` section marker.

2. **Execute Parsing**
    - Back up the old JSON first so you can diff: `cp src/content/publications.json /tmp/pubs-before.json`
    - Run: `python3 scripts/parse_latex_publications.py` (optional arg overrides the source path).
    - This regenerates `src/content/publications.json`.
    - **Validation** — diff old vs new by title rather than eyeballing counts. Expect entries to be
      *added* and venues to firm up (`accepted` → volume/pages); entries *disappearing* means the
      parser broke on a macro. Also check:
        - Total count moved by the expected amount (e.g. 234 → 235).
        - `\dagger` / `$^\dagger$` rendered as `†` (there are 4 as of Aug 2026).
        - "Books & Chapters" tagged `"type": "book"` (4 of them); journals default to `"type": "journal"`.
        - No leftover LaTeX artifacts (`{`, `\`) and no entries with `year` 0.

3. **Update Frontend Rendering (`src/components/PublicationsList.astro`)**
    - Reads `src/content/publications.json`.
    - **Filtering**: Separate items into `journals` and `books` based on the `type` field.
    - **Sorting** (current convention — keep unless HC asks otherwise):
        - *Head*: Keep the original LaTeX order for the first 20 journal items (respects "selected/highlighted" ordering).
        - *Tail*: Sort the remaining items by `year` (descending).
        - **Books**: Flat list preserving LaTeX order, with its own restarted numbering.
    - **Grouping**: Group journals by year for display, but keep continuous numbering across groups.
    - **Formatting**: No DOI links (removed by request). Authors, title, and venue styled per existing component.

4. **Verification**
    - Run `npm run build` to ensure the site builds.
    - Commit: `git add . && git commit -m "Update publications from [filename]"`.

## Best Practices & Constraints

- **Parser Logic**:
  - Use regex for parsing LaTeX rather than strict TeX parsers, to handle non-standard macros gracefully.
  - Always strip LaTeX comments (`%`) before processing to avoid counting commented-out papers.
  - Clean LaTeX artifacts (braces `{}`, styles `\bf`, `\it`) during extraction.
- **Data Structure**:
  - Keep `publications.json` a flat array with a `type` field for categorization — no nesting or separate layout files.
- **Code Style**:
  - Python for data processing scripts; Astro for the frontend component.

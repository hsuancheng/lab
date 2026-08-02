---
name: migrate-legacy-site-to-astro
description: Systematic workflow for migrating a legacy static/DokuWiki/PHP website to Astro using Python scraping and component-based architecture. Use when migrating or re-importing content from a legacy site, or as reference for how this site's structure and design system were built.
---

# Migrate Legacy Website to Astro

A systematic workflow for migrating an existing legacy website (static HTML, DokuWiki, or PHP) to a modern, high-performance [Astro](https://astro.build/) application. This is how the current lab site was originally built — also useful as a reference for its architecture and design system.

## Prerequisites

- Node.js and npm installed.
- Python environment (for scraping scripts) with `requests` and `beautifulsoup4`.
- Access to the legacy website URL.

## Step-by-Step Workflow

### 1. Initialize Astro Project

- Create a new Astro project: `npm create astro@latest` (choose the "Empty" template for full control).
- This project uses vanilla scoped styles — no Tailwind/React integrations.
- **Structure**:
  - `src/components`: UI components (Hero, Cards, Lists).
  - `src/layouts`: Layout wrappers (`BaseLayout.astro`).
  - `src/pages`: Route definitions (`index.astro`, `news.astro`, etc.).
  - `src/content`: Data storage (JSON files).

### 2. Content Migration (ETL Pipeline)

Create a Python script (e.g., `scripts/scrape_site.py`) to extract content from the legacy site into structured JSON.

- **Libraries**: `requests` to fetch HTML, `BeautifulSoup` (`bs4`) to parse.
- **Target Data**:
  - **News/Events**: dates, titles, summaries, links → `src/content/news.json`.
  - **People/Team**: names, roles, emails, photos; group by role (PI, Members, Alumni) → `src/content/people.json`.
  - **Publications**: use the `import-publications-from-latex` skill if a LaTeX source exists.
- **Key Logic**:
  - Use specific CSS selectors or IDs (e.g., `id="news"`, `class="member-list"`) to locate content.
  - Clean text with `unicodedata.normalize` to handle encoding issues.
  - Handle relative URLs by prepending the `BASE_URL`.

### 3. Component Architecture

- **BaseLayout** (`src/layouts/BaseLayout.astro`):
  - `<head>` metadata (SEO, Google Fonts).
  - Navigation bar (responsive, glassmorphism style).
  - Footer (dynamic year, copyright).
  - `<slot />` for page content.
- **Data-Driven Components**:
  - `NewsList.astro`: maps over `news.json` items.
  - `PeopleGrid.astro`: renders profile cards from `people.json`.
  - `ResearchHighlights.astro`: cards for key research areas.

### 4. Visual Design System ("QIQB Style")

- **Typography**: Google Fonts — **Outfit** for headings, **Inter** for body — imported in `BaseLayout`.
- **Color Palette**: CSS variables for primary/secondary colors in `<style is:global>`.
- **Effects**:
  - **Mesh Gradients**: animated CSS radial gradients for hero backgrounds.
  - **Glassmorphism**: `backdrop-filter: blur()` with semi-transparent backgrounds for cards and navbars.
  - **Micro-interactions**: `transform: translateY` and `box-shadow` on hover.

### 5. Deployment

- **Configuration** (`astro.config.mjs`):
  - `site` = production URL (e.g., `https://hsuancheng.github.io`).
  - `base` = subdirectory if applicable (e.g., `/lab`).
- **GitHub Pages**:
  - `.github/workflows/deploy.yml` using the official `withastro/action`.
  - Push to GitHub and enable Pages (Source: GitHub Actions).

## Best Practices

- **Separation of Concerns**: content (JSON) separate from presentation (Astro components).
- **Atomic Components**: small, focused components rather than monolithic page files.
- **Scraping Resilience**: try/except error handling in scraping scripts; verify JSON output before building.

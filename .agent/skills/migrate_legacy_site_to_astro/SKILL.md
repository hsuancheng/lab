---
name: migrate_legacy_site_to_astro
description: Guide the migration of a legacy static or DokuWiki website to a modern Astro application using content scraping and component-based architecture.
---

# Migrate Legacy Website to Astro

This skill provides a systematic workflow for migrating an existing legacy website (e.g., static HTML, DokuWiki, or PHP) to a modern, high-performance [Astro](https://astro.build/) application.

## Prerequisites

- Node.js and npm installed.
- Python environment (for scraping scripts) with `requests` and `beautifulsoup4`.
- Access to the legacy website URL.

## Step-by-Step Workflow

### 1. Initialize Astro Project

- Create a new Astro project: `npm create astro@latest`.
- Choose the "Empty" template for full control.
- Install necessary integrations (e.g., `@astrojs/react` or `@astrojs/tailwind` if needed, though this workflow uses vanilla CSS modules/scoped styles).
- **Structure**:
  - `src/components`: UI components (Hero, Cards, Lists).
  - `src/layouts`: Layout wrappers (`BaseLayout.astro`).
  - `src/pages`: Route definitions (`index.astro`, `news.astro`, etc.).
  - `src/content`: Data storage (JSON files).

### 2. Content Migration (ETL Pipeline)

Create a Python script (e.g., `scripts/scrape_site.py`) to systematically extract content from the legacy site and save it as structured JSON.

- **Libraries**: Use `requests` to fetch HTML and `BeautifulSoup` (`bs4`) to parse it.
- **Target Data**:
  - **News/Events**: Extract dates, titles, summaries, and links. Save to `src/content/news.json`.
  - **People/Team**: Extract names, roles, emails, and photos. Group by role (PI, Members, Alumni). Save to `src/content/people.json`.
  - **Publications**: (Optional) Use scraping or the specialized `import_publications_from_latex` skill if a LaTeX source exists.
- **Key Logic**:
  - Use specific CSS selectors or IDs (e.g., `id="news"`, `class="member-list"`) to locate content.
  - Clean text using `unicodedata.normalize` to handle encoding issues.
  - Handle relative URLs by prepending the `BASE_URL`.

### 3. Component Architecture

Develop reusable Astro components to render the JSON data.

- **BaseLayout**: Create a global layout file (`src/layouts/BaseLayout.astro`) containing:
  - `<head>` metadata (SEO, Google Fonts).
  - Navigation Bar (responsive, glassmorphism style).
  - Footer (dynamic year, copyright).
  - `<slot />` for page content.
- **Data-Driven Components**:
  - `NewsList.astro`: Import `news.json` and map over items to render news cards or rows.
  - `PeopleGrid.astro`: Import `people.json` and render profile cards with images and links.
  - `ResearchHighlights.astro`: Static or data-driven cards for key research areas.

### 4. Visual Design System

Apply a modern, premium aesthetic (e.g., "QIQB Style").

- **Typography**: Use Google Fonts (e.g., **Outfit** for headings, **Inter** for body). Import them in `BaseLayout`.
- **Color Palette**: Define CSS variables for primary/secondary colors in a global stylesheet or `<style is:global>`.
- **Effects**:
  - **Mesh Gradients**: Use animated CSS radial gradients for hero backgrounds.
  - **Glassmorphism**: Use `backdrop-filter: blur()` and semi-transparent backgrounds for cards and navbars.
  - **Micro-interactions**: Add `transform: translateY` and `box-shadow` on hover.

### 5. Deployment

* **Configuration**: Update `astro.config.mjs`:
  - Set `site` to the production URL (e.g., `https://username.github.io`).
  - Set `base` if deploying to a subdirectory (e.g., `/repo-name`).
- **GitHub Pages**:
  - Create `.github/workflows/deploy.yml` using the official `withastro/action`.
  - Push code to GitHub and enable Pages in repository settings (Source: GitHub Actions).

## Best Practices

* **Separation of Concerns**: Keep content (JSON) separate from presentation (Astro components).
- **Atomic Components**: Build small, focused components (e.g., `MemberCard`) rather than monolithic page files.
- **Scraping Resilience**: Add error handling in scraping scripts (try/except blocks) and verify JSON output before building.

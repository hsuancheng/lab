Status: active

# lab — Huang Lab Website

Astro 4 static site for the Huang Lab, deployed to GitHub Pages.

- **Live**: https://hsuancheng.github.io/lab
- **Repo**: https://github.com/hsuancheng/lab (`origin`, branch `main`)
- **Deploy**: automatic on push to `main` via `.github/workflows/deploy.yml` (`withastro/action`)

Originally scaffolded with Antigravity; the two workflow skills it left in `.agent/skills/`
have been converted to `.claude/skills/` (the `.agent/` copies are kept as the original record).

## Commands

| Command         | Action                                    |
| :-------------- | :---------------------------------------- |
| `npm run dev`   | Dev server at `localhost:4321/lab`        |
| `npm run build` | Build to `dist/` — run before committing  |
| `npm run preview` | Preview the production build             |

## Architecture

Content lives as JSON, presentation as Astro components. Never hardcode content into components.

```
sources/              ← LaTeX inputs, canonical & undated (git history = the archive)
├── pub.tex               publication list → feeds publications.json
└── cv.tex                HC's CV — gitignored, local only (see below)
src/
├── content/          ← data (JSON, the source of truth for rendering)
│   ├── publications.json   generated from sources/pub.tex — do not hand-edit
│   │                       [{ year, title, authors, venue, doi, note, type }] (~234 entries)
│   ├── people.json         { pi: [...], members: [...], alumni: [...] }
│   └── news.json           [{ date, title, summary, link }]
├── components/       ← Hero, PublicationsList, PeopleGrid, NewsList, ResearchHighlights
├── layouts/BaseLayout.astro   ← head/SEO, fonts, nav, footer, <slot />
└── pages/            ← index, people, publications, news, contact
scripts/              ← Python ETL (LaTeX parser, legacy-site scraper)
```

## Key conventions

- **Publications are generated.** `src/content/publications.json` comes from
  `python3 scripts/parse_latex_publications.py` reading `sources/pub.tex`. Edit the LaTeX or the
  parser, never the JSON directly. Use the `import-publications-from-latex` skill.
- **LaTeX sources are undated and overwritten in place.** When HC sends a new `pub-YYYYMMDD.tex`,
  copy it over `sources/pub.tex` rather than adding a dated file — git history is the archive, and a
  stable filename keeps the parser path fixed. Pre-git dated versions live in `~/work/mypubs/`.
- **This repo is public.** `sources/cv.tex` is gitignored because commented-out lines in it hold
  personal details (birth date, family) that never appear in the compiled PDF but would be readable
  in the repo. If CV content is ever needed on the site, extract the specific fields into JSON —
  don't commit the `.tex`. Apply the same check to any new source file before tracking it.
- **Publication ordering** (deliberate, don't "fix" it): first 20 journal entries keep the LaTeX order;
  the rest sort by year descending. Books & Chapters are a separate section with restarted numbering.
  DOI links were dropped by request: the parser emits `doi: ""` for every entry, so the component's
  DOI block never renders. Keep it that way unless HC asks for DOIs back.
- **`base: '/lab'`** is set in `astro.config.mjs` — internal links and asset paths must respect it.
- **Styling** is vanilla scoped CSS (no Tailwind). Design system: Outfit headings / Inter body,
  mesh-gradient hero, glassmorphism cards and navbar, `translateY` + shadow hover.
- **Python** scripts run under the project `.venv/`; the LaTeX parser is stdlib-only, so `python3` suffices.
- **Commit messages in English.** Verify with `npm run build` before committing.

## Skills

- `import-publications-from-latex` — update publications from a new `pub-*.tex`
- `migrate-legacy-site-to-astro` — legacy content migration; also documents the design system

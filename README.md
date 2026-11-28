# Earlyseed Ventures website

The public site for [Earlyseed Ventures](https://esvwebsite.vercel.app). It's plain HTML, CSS and vanilla JS, with no framework and no JS dependencies. Small Python scripts build the inner pages from templates and data files.

## Run locally

```bash
python tools/serve.py
# open http://127.0.0.1:5173
```

Vercel serves the repo root as it is. A push to `main` deploys.

Addresses have no `.html`: `about.html` is served at `/about`, and `/about.html` redirects there (`"cleanUrls"` in `vercel.json`). Write internal links either way in templates; the build strips `.html` from every page and `tools/serve.py` behaves like Vercel. `vercel.json` also redirects the old Wix addresses and keeps the `vercel.app` preview out of search results. Missing addresses show `404.html`.

## How the repo is laid out

```
index.html, *.html   The pages. Their file names, without .html, are the public URLs, so they stay at the root.
                     index.html is edited by hand; every other page is built (see below).
css/styles.css       All styles: brand tokens, layout, motion, accessibility preferences
js/main.js           All behaviour: header, search, menus, carousels, reveals, interactive tools and diagrams
assets/              Web-ready images, logos, icons and fonts (written by the scripts in tools/)
tools/               Build scripts, page templates and the content data files (not deployed)
docs/                Working notes: pre-launch review, form specs; docs/archive/ holds finished briefs
source/              Local only, gitignored: original logos, photos and brand files the scripts read from
sitemap.xml, robots.txt   Written by the build
```

## Building the pages

Everything except `index.html` is generated. Edit the template or data, then run:

```bash
python tools/build.py
```

This writes every inner page from `index.html`'s head, header and footer plus each page's own content. It also adds titles, descriptions, structured data and `sitemap.xml`. Finally it stamps the CSS and JS links with a hash of their contents (`styles.css?v=...`), so visitors get a fresh copy only when a file has changed. Running it twice in a row changes nothing.

Where each page's content lives:

| Pages | Template | Content |
|---|---|---|
| `about.html` | `tools/about/main.html` | |
| `team.html`, `team-<slug>.html` | `tools/team/main.html`, `profiles.py` | `tools/team/profiles.json` |
| `portfolio.html`, `portfolio-<slug>.html` | `tools/portfolio/` | `companies.json`, `logos.json`, `photos.json` |
| `perspectives.html`, `perspective-<slug>.html` | `tools/perspectives/` | `posts.json`, article bodies in `posts/`, cover art in `art.py` |
| `tools.html`, `tool-<slug>.html` | `tools/toolkit/` | `tools.json`, each tool in `pages/` |
| `events.html`, `event-<id>.html` | `tools/events/` | `events.json` |
| `careers.html`, `life-<id>.html` | `tools/careers/` | `openings.json`, `stories.json` |
| `press.html` | `tools/press/` | `press.json` |
| `bootcamps.html`, `invest.html`, `prologue.html` | `tools/<page>/main.html` | |
| Titles, descriptions, sitemap | `tools/seo/seo.py` | |

Notes in HTML comments (`<!-- -->`) inside the templates are stripped from the published pages.

## Images and logos

The originals live in `source/` (gitignored). These scripts turn them into web-ready files in `assets/`:

| Script | Reads | Writes |
|---|---|---|
| `python tools/team/photos.py` | `source/Founder Photos/`, `source/Team Photos/cleaned/` | `assets/team/` portraits on sand |
| `python tools/portfolio/assets.py` | `source/Logos/Companies/`, `source/Founder Photos/companies/` | balanced company logos and founder photos |
| `python tools/logos/build.py` | `source/Logos/` | campus, portfolio and affiliation logos |
| `python tools/favicon/build.py` | `source/favicon source.png` | favicons |
| `tools/hero-layers/` | `source/Brand Assets/New v2.png` | the homepage hero collage ([details](tools/hero-layers/README.md)) |

Run `python tools/build.py` afterwards so the pages pick up the new files.

## Brand

Colours, defined on `:root` in `css/styles.css`: crema `#F7ECE2`, fair `#F4F4F4`, slate `#A39B95`, sand `#D3C1A9`, bronze `#D5AE8F`, golden glow `#CB8C7C`, pastel purple `#CEAAFD`, purple `#745FFD`, deep ink `#4B38D8`.

Type: Sorts Mill Goudy for headings and editorial copy (with lining numbers), Inter for UI text.

Copy: no em or en dashes, and no numbers that aren't from a source.

## Interaction notes

Motion follows Apple's *Designing Fluid Interfaces* principles:

- **Press feedback** fires on pointer-down (`:active` scale), never on release.
- **Portfolio strip** tracks the pointer 1:1, projects flick momentum, rubber-bands past the edges and springs to the nearest logo. Trackpad scroll and arrow keys also work.
- **Header** turns into a translucent material only once content scrolls beneath it.
- **Search** grows out of its icon. Press `/` to open it.
- **Scroll reveals** use `data-reveal`; elements animate when they gain `.is-in`.
- `prefers-reduced-motion`, `prefers-reduced-transparency` and `prefers-contrast` are all handled.

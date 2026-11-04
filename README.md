# Earlyseed Ventures — Website

Static homescreen for [Earlyseed Ventures](https://github.com/EarlySDE-Hades/ESV-Website). No build step and no dependencies: plain HTML, CSS and vanilla JS.

## Run locally

```bash
python -m http.server 5173
# open http://127.0.0.1:5173
```

Any static host works for deployment (Vercel, Netlify, GitHub Pages). The site root is the repo root.

## Structure

```
index.html          Homescreen markup
css/styles.css      Brand tokens, layout, motion, accessibility preferences
js/main.js          Header material, search, mobile menu, portfolio strip physics, scroll reveals
assets/brand/       ESV wordmark (transparent PNG, dark + light)
assets/hero/        Cropped collage layers, responsive WebPs and a flat fallback
tools/hero-layers/  Offline extraction, masks and image audits
assets/logos/       Drop campus + portfolio logo files here (see below)
```

## Brand tokens

Taken from the ESV colour palette and defined on `:root` in `css/styles.css`:
crema `#F7ECE2`, fair `#F4F4F4`, slate `#A39B95`, sand `#D3C1A9`, bronze `#D5AE8F`,
golden glow `#CB8C7C`, pastel purple `#CEAAFD`, purple `#745FFD`.

Type: Sorts Mill Goudy (headings and editorial copy), Inter (UI), Cormorant Garamond 600 (stat figures).

## Adding logos

Campus partner and portfolio logos currently render as text wordmarks. To use real artwork, add files under
`assets/logos/campus/` or `assets/logos/portfolio/` and replace each `<span class="wordmark">…</span>` in
`index.html` with:

```html
<img src="assets/logos/portfolio/skyroot.svg" alt="Skyroot Aerospace" draggable="false" />
```

SVG is preferred; otherwise use a transparent PNG at 2× display size (about 84px tall in the portfolio strip, 72px tall in the campus row).
The section badges (handshake, angel wings) and the founder and investor icons are SVG placeholders. Swap them for the exported illustrations.

## Hero collage

The homepage assembles six paper cutouts from `Brand Assets/New v2.png` alongside
an inline SVG sun and sparkles. People retain their original opaque pixels in
lossless desktop exports. All positions come from an offline manifest and are
embedded in HTML; there are no runtime dependencies or build steps.

See [the layer tooling](tools/hero-layers/README.md) for the one-command extraction
pipeline and [the acceptance report](docs/hero-collage-report.md) for measured results.
The entrance reuses the site's springs and runs once after image decoding and
visibility, then adds occasional twinkles and small pointer/scroll offsets.
`?slow=10` slows assembly for inspection. Reduced motion shows a static composition;
no JavaScript shows final layers, and a failed layer switches to the flat image.

## Interaction notes

Motion follows Apple's *Designing Fluid Interfaces* principles:

- **Press feedback** fires on pointer-down (`:active` scale), never on release.
- **Portfolio strip** tracks the pointer 1:1, projects flick momentum (`project()`, deceleration 0.998),
  rubber-bands past the edges, and springs to the nearest logo. Springs take damping and response and can be
  grabbed mid-flight. Trackpad horizontal scroll and ← → keys also work.
- **Header** turns into a translucent material only once content scrolls beneath it, with a soft edge instead of a divider.
- **Search popover** grows out of its icon and leaves the same way. Press `/` to open it.
- `prefers-reduced-motion`, `prefers-reduced-transparency` and `prefers-contrast` are all handled.

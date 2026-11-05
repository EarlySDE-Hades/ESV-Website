# Codex brief: Team page affiliation logos

## Goal
On `team.html`, each leader card shows a row of affiliation logos under their tags, as on the original "Meet the Core Team" slide. Turn the source files in `Logos/Team/` into web-ready **transparent WebP** files and add them to the page.

`Logos/` is gitignored. Commit only the generated files in `assets/logos/team/`.

## Source files → output slug

| # | Source (`Logos/Team/…`) | Slug | Alt text | What it needs |
|---|---|---|---|---|
| 1 | `Ascent.jpg` (447², RGB) | `ascent` | Ascent | Remove white background, trim |
| 2 | `bluearc_advisors_llp_logo.jpg` (200², RGB) | `bluearc` | BlueArc Advisors | Remove white background, trim. The wordmark is small, so keep every pixel and never upscale |
| 3 | `bni-2020-logo-png_seeklogo-378515.png` (600², palette PNG) | `bni` | BNI | Convert to RGBA. Its background is opaque white, so remove it and trim |
| 4 | `Corporate Connections.jpg` (447², RGB) | `corporate-connections` | Corporate Connections | Remove white background, trim |
| 5 | `mnco_logo.jpg` (200², RGB) | `mn-co` | MN &amp; Co. Chartered Accountants | Remove white background, trim |
| 6 | `New-logo-of-CA.png` (1200×628, RGBA but opaque white) | `ca-india` | CA India | Remove white background, trim |
| 7 | `Yaha Waters.jpg` (200², RGB) | `yaha-water` | Yaha Water Systems | Remove white background **and** the thin grey frame along the left and right edges, then trim |
| A | `cropped-FINAL-LOGO.png` (already transparent) | `vis-legis` | Vis Legis Law Practice | Trim only |
| B | `RotaryMBS-Simple_RGB.png` (already transparent) | `rotary` | Rotary | Trim only |
| C | `WILL_logo_negativo_340.png` (340×62) | `will` | Worldwide Independent Lawyers League | See the note below |

**WILL note:** this is the *negative* artwork. It is pale gold on a solid crema background (235,225,214) and would almost disappear on the site's `#F4F4F4` background.
1. Remove the crema background.
2. Recolour every visible pixel to `#1B2A4A`, the dark navy used on the slide, and keep the alpha so the edges stay smooth.
3. Leave a comment in the script saying a positive version should replace this when one is available.

## Background removal: how
- Do it in Python with Pillow, in the existing `tools/logos/build.py`. No new dependencies (numpy is fine if it's already installed).
- **Flood-fill from the image edges** for pixels near white (each channel ≥ 245), so white areas *inside* a logo survive. Examples are BNI's white "i" dot and the white counters in letters.
- **Anti-aliased edges:** don't leave a white halo. For edge pixels next to the removed region, use colour-to-alpha (un-premultiply against white): `alpha = max over channels of (255 - c) / (255 - 0)`, then recover the colour. Check the edges at 400% zoom on a dark background.
- Then trim to the alpha bounding box, using the script's existing crop-to-visible-pixels logic.

## Pipeline
1. Add a `TEAM` list to `tools/logos/build.py`, next to `PORTFOLIO` and `CAMPUS`, using the slugs and alt text above.
2. Write to `assets/logos/team/<slug>.webp`, as WebP with alpha, at quality about 90.
3. Sizing:
   - Reuse the script's visual-area balancing.
   - Display box: about **28px tall** for wide wordmarks and up to **40px** for square marks (Yaha, Corporate Connections, CA India), with a max width of about 120px.
   - Export at 2× the display size and never upscale. BlueArc and MN&Co. are tiny sources, so export them at their native size.
4. Print the `<img>` markup with correct `width`/`height` attributes, plus `loading="lazy" decoding="async"`.

## Who gets which logos (from the slide, in order)

| Person (card in `tools/team/main.html`) | Logos |
|---|---|
| CA Monica Gupta | corporate-connections, rotary, ca-india |
| CA Manan Patel | ca-india, mn-co, bni |
| CA Nimit Shah | bluearc, bni, ca-india |
| Adv. Rahul Hingmire | vis-legis, ascent, will |
| Sudhir Mehta | yaha-water, rotary |

## Markup
1. Edit **`tools/team/main.html`, not `team.html`**. In each `<li class="person">`, after the `person__tags` list or after the bio if there are no tags, add:

   ```html
   <ul class="person__logos" role="list" aria-label="Affiliations">
     <li><img src="assets/logos/team/rotary.webp" alt="Rotary" width="…" height="…" loading="lazy" decoding="async" /></li>
     …
   </ul>
   ```

2. Remove the `<!-- Affiliation logos go here -->` comment.
3. Rebuild the page with `python tools/team/build.py`. That script generates `team.html`, so never hand-edit it.

## CSS
Append the following to the "Team page — Leadership" block at the end of `css/styles.css`:

```css
.person__logos {
  display: flex; flex-wrap: wrap; align-items: center;
  gap: 14px 18px; margin-top: 16px;
}
.person__logos img { display: block; width: auto; max-height: 40px; max-width: 120px; object-fit: contain; }
```

- The tags row uses `margin-top: auto` so the tags line up along the bottom of the row. Keep that.
- The logos sit directly under the tags.
- For cards **without** tags (Nimit, Sudhir), make sure the logo rows still line up with the other cards. Either give `.person__logos` the `margin-top: auto` when it directly follows the bio, or wrap tags and logos together in a `.person__foot` with `margin-top: auto`.

Then bump the cache-busting `?v=` number on `css/styles.css` and `js/main.js` in `index.html`, and rebuild `team.html`.

## Acceptance checks
- [ ] 10 files in `assets/logos/team/`, each under 20 KB, with transparent corners (alpha = 0 at pixel 0,0).
- [ ] No white boxes or halos when viewed on `#F4F4F4` or on a dark background.
- [ ] BNI's white details and the white inside other marks are intact.
- [ ] WILL is readable, in dark navy.
- [ ] At 1440px wide, the five cards stay in one row and the logo rows line up across them.
- [ ] At 390px there's no horizontal scroll, and the logos wrap neatly.
- [ ] No console errors on `team.html` or `index.html`.
- [ ] Commit the build script change, the assets, `tools/team/main.html`, `team.html`, `css/styles.css` and `index.html`. Do not commit anything under `Logos/`.

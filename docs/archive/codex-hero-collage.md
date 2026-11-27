# Task: Animated layered collage for the homepage hero

You are working in the Earlyseed Ventures (ESV) website repo. Replace the current hero video with a layered paper-collage illustration that **assembles itself once on page load, then rests**, with light ambient life afterward. Read this whole brief before starting. Do the work in the order given, and check every item in the acceptance checklist at the end.

---

## 1. Why this approach (so you can make good judgement calls)

- The audience is Indian founders (who want to raise) and HNI and family-office investors. The hero must build **trust and clarity** first and draw attention second.
- The headline under the image reads *"Building a self-reliant India, one founder at a time."* The collage piecing itself together **is that idea made visible**: building, one piece at a time. Every motion decision should serve that story.
- The motion principles come from Apple's *Designing Fluid Interfaces* (WWDC 2018):
  - **Do:** one purposeful entrance, then stillness; springs instead of fixed-duration easing; motion only on `transform` and `opacity`; a full reduced-motion fallback.
  - **Don't:** endless slow oscillation (anything looping near 0.2 Hz), animating faces, layout-triggering properties, or blocking input or the headline behind the animation.
- AI video was rejected: it was heavy (~9 MB), had background colour mismatch, risked uncanny face motion and had a loop seam. **Do not animate any person's face or body. People stay exactly as photographed.**

---

## 2. Repo context

- **Stack:** static site with plain HTML, CSS and vanilla JS. **No build step and no runtime dependencies; keep it that way.** Fonts come from Google Fonts.
- **Run locally:** `python -m http.server 5173`, then open `http://127.0.0.1:5173`.
- **Files:**
  - `index.html`: page markup. The hero is `<section class="hero" id="about">`.
  - `css/styles.css`: brand tokens on `:root`, sections in order, responsive rules, then accessibility media queries at the end.
  - `js/main.js`: one IIFE. It already contains `createSpring()` (a damping/response spring), `project()`, `rubberband()`, and the `reduceMotion` media query. **Reuse these and don't duplicate them.**
- **Brand tokens** (already in `:root`): `--fair: #F4F4F4` (page background), `--crema #F7ECE2`, `--slate #A39B95`, `--sand #D3C1A9`, `--bronze #D5AE8F`, `--golden-glow #CB8C7C`, `--pastel-purple #CEAAFD`, `--purple #745FFD`. Easing tokens: `--ease-out`, `--ease-in`.
- **Current hero (to be removed):** a `<figure class="hero-media" data-hero-media>` with a `<video>` and a play/pause button, styled by `.hero-media*` rules in CSS, driven by `initHeroVideo()` in JS, with the file in `assets/video/hero.mp4`. These changes may be uncommitted in the working tree; that's expected.
- `Brand Assets/` and `Figma Design/` are **gitignored** source folders. Anything the site serves must be written to `assets/`.

---

## 3. Source image

- **File:** `Brand Assets/New v2.png`. It's RGB, **2114 × 846 px**, on a flat background of exactly `#F4F4F4`, which matches the page.
  - `Brand Assets/New.png` (2114 × 744) is an earlier crop of the same artwork with less headroom. Use `New v2.png`.
- The bottom of the collage is a **straight horizontal baseline at about y = 824**. Everything sits on it, and there's roughly 22 px of background below it.

### Element inventory

Coordinates are in source pixels and approximate: verify them, then refine. The table runs back to front (z-order).

| z | id | element | approx. bbox (x0, y0 → x1, y1) | notes |
|---|----|---------|-------------------------------|-------|
| 1 | `sun` | yellow disc | centre ≈ (770, 376), r ≈ 156 | Flat colour. **Rebuild as an inline SVG circle**; sample the exact yellow from the image. Occluded by the dome and the women. |
| 2 | `dome` | domed monument, including its arcaded base | (580, 116 → 1480, 824) | Largest layer. Occluded by the women, the plant and possibly the young woman. |
| 3 | `building` | white modern building | (1550, 396 → 1950, 824) | Occluded by the young woman on its left edge. |
| 4 | `plant` | banana-leaf plant and yellow flower | (1106, 292 → 1444, 824) | In front of the dome. |
| 5 | `women` | two women in saris with basins, plus the small flowers at their feet | (600, 356 → 1112, 824) | Keep as **one** layer. In front of the sun and the dome. |
| 6 | `scientist` | scientist, microscope and cable | (196, 480 → 620, 824) | Front-left. Check whether it overlaps `women`. |
| 7 | `student` | young woman in a yellow shirt with a red folder | (1416, 466 → 1724, 824) | Front-right, in front of the building and the plant. |
| 8 | `sparkle-1`, `sparkle-2` | thin dark four-point sparkle stars | ≈ (540, 368) and ≈ (1466, 256), ~40–60 px | **Rebuild as inline SVG**: thin strokes, same dark grey as the image. |

---

## 4. Step 1 — Extract the layers (reproducible pipeline)

Create `tools/hero-layers/` containing a script (Python preferred; Node is fine) and a short `README.md` saying how to re-run it. The pipeline must be re-runnable from `Brand Assets/New v2.png` so the art can be updated later.

1. **Segment** each raster element (`dome`, `building`, `plant`, `women`, `scientist`, `student`) into its own RGBA layer.
   - The background is a flat `#F4F4F4`, so colour-keying gives the outer silhouette of the whole collage cheaply.
   - Separating elements that touch each other needs real segmentation. Use any reliable method: SAM / rembg / U²-Net, or hand-tuned polygon masks stored as JSON in the tools folder.
   - Hand-authored masks are acceptable if they're precise.
2. **Edge quality:** cut-out edges must be clean.
   - No `#F4F4F4` or white halo, no jaggies, no lost hair detail (the student's curly hair is the hard case).
   - Use a 1 px feather at most. Decontaminate edge colour (un-premultiply the background out of semi-transparent pixels).
3. **Fill hidden regions.** Back layers have regions hidden behind front layers: the dome behind the women and the plant, and the building behind the student.
   - Those regions **become visible during the entrance animation** before the front layers land.
   - Fill them plausibly by inpainting: OpenCV `inpaint` (Telea) at minimum, or LaMa if available. Extend architecture lines where you can.
   - They're only seen in motion for a fraction of a second, so "believable at a glance" is the bar. A visible empty hole or a hard smear is not acceptable.
4. **Export:**
   - Write `assets/hero/<id>.webp`: lossless or quality ≥ 90, with alpha, **cropped to each layer's bounding box plus 4 px padding**.
   - Also export a half-resolution version, `assets/hero/<id>@1x.webp` (source ÷ 2), for small screens.
   - Write `assets/hero/manifest.json` listing every layer's `id`, `z`, `x`, `y`, `w`, `h` in source-canvas pixels (2114 × 846). These drive positioning.
   - Export a flat fallback, `assets/hero/collage-flat.webp`: the original composite at web quality, about 1600 px wide.
5. **Verify by recompositing:**
   - Have the script recomposite all layers (rebuilding the SVG sun and sparkles as rasters for the check) over `#F4F4F4`.
   - Diff the result against the source. **Mean absolute error must be ≤ 2 per channel**, with no region larger than 4 × 4 px showing a visible difference.
   - Save `tools/hero-layers/out/recomposite.png` and `diff.png` (gitignore `out/`). Report the numbers.
6. **Weight budget:** all layers for one breakpoint together should be **≤ 600 KB on desktop (2×) and ≤ 250 KB on mobile (1×)**. If you go over, lower WebP quality on the large layers before anything else.

---

## 5. Step 2 — Hero markup and layout

Replace the video `<figure>` with:

```html
<div class="hero__media-wrap">
  <div class="collage" data-collage role="img"
       aria-label="Collage of India's builders: a scientist at a microscope, two women carrying produce, a student with a folder, a historic domed monument, a modern building and a flowering plant, under a rising yellow sun.">
    <!-- svg sun, raster layers in z-order, svg sparkles; all alt="" / aria-hidden -->
  </div>
</div>
```

- **Positioning:**
  - The `.collage` box has `aspect-ratio: 2114 / 846`.
  - Each layer is absolutely positioned **in percentages** from the manifest: `left = x / 2114`, `top = y / 846`, `width = w / 2114`.
  - Write those values into the HTML or CSS custom properties directly. Don't fetch the manifest at runtime.
- **Images:**
  - Each `<img>` gets `srcset="…@1x.webp 1057w, ….webp 2114w"`, a correct `sizes`, explicit `width`/`height` (to avoid layout shift), `decoding="async"`, `alt=""` and `draggable="false"`.
- **Width:**
  - Desktop: up to the same 1160 px container the header uses.
  - Phones (≤ 720 px): edge to edge, with no side gutter.
  - The collage has no frame, border, shadow or rounded tile. It **sits directly on the page**, and its background is the page.
- **Order:** the headline and CTAs stay below the collage, as now.
- **No-JS and image-failure state:** without JS, the layers show in their final composed positions. If any layer fails to load, swap the whole collage for `collage-flat.webp`.
- **Remove the video everywhere:**
  - the `<video>` and toggle markup
  - all `.hero-media*` CSS, including the related rules in the reduced-motion, reduced-transparency and mobile media queries
  - `initHeroVideo()` and its call
  - the `assets/video/` folder

---

## 6. Step 3 — Motion spec

### 6.1 Entrance (plays once per page load)

**Trigger.** Wait until every layer has decoded (`Promise.all(img.decode())`) and the collage is at least 25% in view, with a **1500 ms timeout**.
- If the timeout fires, show everything in its final state with a 250 ms opacity fade and skip the choreography.
- Never replay it on scroll-back.

**Before it runs,** layers sit in their *from* state. Do this via a class set by JS (e.g. `.collage.is-pre`) so no-JS users never see hidden layers.

**Springs.** Use the existing `createSpring()` (critically damped unless stated otherwise). Alternatively use WAAPI with a `linear()` easing sampled from the same spring, falling back to `cubic-bezier(0.22, 1, 0.36, 1)`.
- Motion: `transform` and `opacity` only.
- Use `transform-origin: 50% 100%` (bottom centre), so pieces feel like they're being laid down onto the baseline.

| start (ms) | layer | from → to | spring (damping, response s) |
|---|---|---|---|
| 0 | `dome` | opacity 0 → 1, translateY 28px → 0, scale 0.985 → 1 | 1.0, 0.70 |
| 140 | `sun` | rises from behind the dome: translateY 45% of its height → 0, opacity 0 → 1 | 0.9, 0.85 |
| 220 | `building` | opacity 0 → 1, translateX 28px → 0 | 1.0, 0.60 |
| 320 | `plant` | opacity 0 → 1, scaleY 0.9 → 1 (grows from base) | 1.0, 0.60 |
| 420 | `women` | opacity 0 → 1, translateY 20px → 0 | 1.0, 0.55 |
| 500 | `scientist` | opacity 0 → 1, translateY 20px → 0 | 1.0, 0.55 |
| 580 | `student` | opacity 0 → 1, translateY 20px → 0 | 1.0, 0.55 |
| 900 | sparkles | scale 0 → 1, rotate −45° → 0°, opacity 0 → 1 | 0.8, 0.50 |

- **Total ≈ 1.6 s.** The headline and CTAs **must not wait** for the collage; they keep their existing `data-reveal` behaviour.
- **"Paper being placed" detail (optional):** during the entrance only, each raster layer can carry a soft drop shadow that tightens as it lands, roughly `drop-shadow(0 10px 14px rgba(40,30,25,.14))` → `drop-shadow(0 1px 1px rgba(40,30,25,.08))`.
  - Remove the filter entirely once the layer settles.
  - **Drop this detail if it causes dropped frames** at 1280 px wide on a mid-range laptop. Smoothness beats ornament.
- **Clean up:** remove `will-change` from every layer once the entrance completes.

### 6.2 Ambient life (after the entrance settles)

- **Sparkle twinkle:** every 5–9 s (randomised, never both at once), one sparkle does scale 1 → 1.3 → 1 with a 45° rotation over ~900 ms. **Not a continuous loop.** Stop while the collage is off-screen or the tab is hidden.
- **Pointer depth:** only on `(hover: hover) and (pointer: fine)`.
  - Moving the pointer over the hero shifts layers by a depth factor, at most **±4 px for `sun`/`dome`, ±7 px for `building`/`plant`, ±10 px for the people**, in the direction of the pointer offset from the collage centre.
  - Smooth it with a critically damped spring (response ~0.6 s), one spring per axis. On `pointerleave`, spring back to 0.
  - Must start from the current value, so it can be interrupted at any time.
- **Scroll depth:** as the hero scrolls out of view, back layers lag slightly behind front layers, at most **12 px of difference** across the hero's full scroll-out.
  - Drive it with `requestAnimationFrame` and passive listeners, and only while the hero intersects the viewport.
- **Never animate the sun's brightness in a loop**, and add no other ambient motion.

### 6.3 Reduced motion and accessibility

- `prefers-reduced-motion: reduce`: no choreography, parallax or twinkle. The collage appears in its final state; a single ≤ 200 ms opacity fade of the whole collage is allowed. Listen for changes to the preference at runtime.
- `prefers-reduced-transparency` / `prefers-contrast`: nothing special is needed for the collage itself, but don't break the existing rules.
- Never block input, scrolling or the CTAs during the entrance.

---

## 7. Constraints

- No frameworks, bundlers or npm runtime packages in the site. Tooling packages inside `tools/hero-layers/` are fine.
- Match the existing code style:
  - CSS: section comment banners, tokens on `:root`, hover styles inside `@media (hover: hover) and (pointer: fine)`.
  - JS: `init*()` functions inside the IIFE, with `$`/`$$` helpers.
- Don't change other sections, copy, fonts or brand colours.
- Animate only `transform` and `opacity` (plus the optional, temporary `filter` above).
- Keep the people pixel-identical to the source: no warping, morphing or face motion.

---

## 8. Acceptance checklist (verify each one and report results)

- [ ] `tools/hero-layers/` regenerates every asset from `Brand Assets/New v2.png` with one command, and its README documents that command.
- [ ] Recomposite error ≤ 2 mean abs per channel, with numbers reported. No visible halos at 200% zoom on the student's hair, the plant leaves or the dome finial.
- [ ] Hidden regions are filled; no holes show during the entrance (check by slowing it 10×, e.g. a debug multiplier in `?slow=10`).
- [ ] At rest, the collage is visually identical to the source image, sitting seamlessly on the `#F4F4F4` page with no visible box or edge.
- [ ] Layer weight is within budget (≤ 600 KB at 2×, ≤ 250 KB at 1×), with sizes reported.
- [ ] The entrance plays once, takes ~1.6 s, runs at 60 fps at 1280 px, and the headline is readable immediately.
- [ ] Pointer depth is smooth, interruptible and springs back; scroll depth is subtle; the twinkle is occasional, not looping.
- [ ] Reduced-motion emulation shows the final collage with no movement.
- [ ] No-JS shows the final collage; a broken layer URL falls back to `collage-flat.webp`.
- [ ] No horizontal overflow at 390 px; works at 1280, 1024 and 390 px wide.
- [ ] Layout shift (CLS) is 0 for the hero; no console errors.
- [ ] The video hero is fully removed (markup, CSS, JS and `assets/video/`).
- [ ] `README.md` updated: replace any hero-video notes with a short "Hero collage" section (pipeline, layers, motion).

## 9. Delivery

- Work on a new branch, `feat/hero-collage`. Commit with clear messages. **Do not push.**
- Finish with a short report:
  - what you built
  - the recomposite error and asset weights
  - anything you couldn't meet, and why
  - screenshots of the rest state at 1280 px and 390 px, plus 3–4 frames from mid-entrance

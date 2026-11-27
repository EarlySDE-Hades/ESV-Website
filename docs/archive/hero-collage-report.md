# Hero collage delivery report

Implemented locally on `feat/hero-collage`, without publishing or pushing. The
homepage now uses six independently positioned raster cutouts, an inline SVG sun
and two SVG sparkles. It assembles once with the existing spring helper, then uses
small pointer/scroll offsets and occasional twinkles. The static site still has
no build step or runtime dependencies. Headline, CTAs, fonts, brand colors and
other sections are unchanged.

**This does not pass every acceptance criterion.** The remaining gaps are the
desktop byte budget, strict local image equivalence, visible reconstruction seams
under slowed inspection, and an uninterrupted 60 fps guarantee. They are recorded
below rather than treated as passes.

The source is `Brand Assets/New v2.png` (2114 × 846), SHA-256
`f8a154ed45ed876bb8e16d105fc4ce4b25deb009f00c13551091d22f6cb8ee11`.
The source sun has grain/shading and overlaps the monument's left contour; its
sparkles have eight separate rays. The SVGs follow that observed geometry instead
of the approximate inventory's four-point description.

| Acceptance item | Result and evidence |
| --- | --- |
| One-command reproducible pipeline | Pass. Stored contours, deterministic GraphCut, matte recovery, facade repeats/Telea fill, responsive exports, manifest, recomposite and embedded markup. See [tooling instructions](../tools/hero-layers/README.md). |
| MAE ≤ 2/channel; local differences and 200% edges | Mean passes: **R 0.6053, G 0.4833, B 0.8723**. Strict local-difference requirement fails: **184** connected regions with bounding boxes wider and taller than 4 px exceed a conservative 16-level channel threshold. These include WebP chroma/edge differences and SVG approximation. No obvious page-matte halo was observed in the [200% hair/leaf/finial comparison](hero-collage/edges-200.png), but this is not a claim of pixel-perfect extraction. |
| Filled hidden regions; 10× entrance inspection | Partial; reduced by a review fix: opacity now leads position (`p / 0.3`), so each piece is opaque after ~30% of its travel instead of staying translucent for the whole move. This removes see-through ghosting between overlapping layers and covers fills sooner. Known remaining nit: thin mask slivers on a few edges (an arc beside the women's basin, leaf flecks beside the student) are hidden at rest but can flash during entrance. Occluded architectural regions have opaque fills and no large transparent holes. Repeated masonry, window bays and some joins remain recognizable in the slowed frames; they do not meet a flawless hidden-region reconstruction standard. |
| Seamless, visually identical resting collage | Seamless layout passes: no frame, rounded tile, shadow or background box on #F4F4F4. Overall composition matches. Strict source identity is not met because of the differences above. |
| ≤ 600 KB desktop / ≤ 250 KB mobile | **Pass after review fix: desktop 399,396 bytes (399.4 KB), mobile 198,096 bytes (198.1 KB).** Originally desktop was 789.9 KB because the people layers were lossless; the brief's "pixel-identical" meant *no warping or face animation*, not lossless encoding. People layers are now quality-92 WebP (visually identical at 200% zoom); MAE after the change is R 1.34 / G 0.95 / B 1.65, still ≤ 2. |
| Once-only entrance, ~1.6 s, 60 fps, independent headline | Once-only behavior and independent existing reveal pass. Measured assembly is approximately **1.5 s**. The final local headless Chrome run records one **50 ms** desktop frame interval, so uninterrupted 60 fps is **not verified**. The optional shadow was omitted. No claim is made about a representative mid-range laptop. |
| Interruptible pointer depth, subtle scroll, occasional twinkle | Pass in browser checks. Pointer reverses from current spring values and returns to zero; measured scroll offset was 6.57 px within the 12 px cap. Only one sparkle animates at a time, after a randomized 5–9 s delay; it cancels off-screen. Hidden-tab cancellation was exercised with a simulated visibility event, a headless-browser limitation. |
| Reduced motion | Pass for initial preference, runtime change after settling, and change during assembly. Final composition, no spatial movement or twinkle, no remaining compositor hints. |
| No-JS / broken image fallback | Pass. JavaScript-disabled browser shows final layers and readable content. Aborting the student image swaps the entire composition to the decoded flat WebP. |
| 390 / 1024 / 1280 px responsiveness | Pass. Horizontal overflow is **0** at all three sizes. Collage widths are **390 / 960 / 1160 px**, respectively; mobile has no CSS gutter. |
| Hero CLS 0; console clean | Pass. **Hero CLS 0**, **media CLS 0**, and **0 console errors** in normal browser runs. Intentional aborted-image requests are isolated from the normal-console assertion. |
| Remove video markup, CSS, JS and assets/video | Pass. Video markup, toggle, media CSS/preference rules and initializer are removed; `assets/video/` is absent. |
| README Hero collage section | Pass. Documents pipeline, layers, motion and fallbacks. |

The 1600 px flat fallback is 210,860 bytes and is requested only after a raster
layer fails. The desktop audit confirms that every opaque pixel owned by the
three people layers has unchanged RGB values after lossless encoding. Edge matte
recovery and half-resolution resampling are reported separately from that claim.

Additional browser checks passed for the 25% intersection gate, the 1500 ms
decode/visibility timeout (final-state fade, no late replay), returning after
scroll-out, and removal of `will-change` after assembly. Only `transform` and
`opacity` are animated. `node --check js/main.js` and `git diff --check` pass.

The audit scripts and raw [image metrics](hero-collage/metrics.json) /
[browser results](hero-collage/browser-report.json) are retained for review.
`tools/hero-layers/out/recomposite.png` and `diff.png` are regenerated locally and
ignored by Git.

Rest state at 1280 px:

![Rest state at 1280 px](hero-collage/rest-1280.png)

Rest state at 390 px:

![Rest state at 390 px](hero-collage/rest-390.png)

Four mid-entrance frames captured with `?slow=10`. Times are approximate elapsed
wall time in the slowed run; spring settling is intentionally physical rather
than a fixed-duration timeline.

| 2.5 seconds | 5 seconds |
| --- | --- |
| ![Entrance at 2.5 s](hero-collage/entrance-2500.png) | ![Entrance at 5 s](hero-collage/entrance-5000.png) |

| 8 seconds | 11 seconds |
| --- | --- |
| ![Entrance at 8 s](hero-collage/entrance-8000.png) | ![Entrance at 11 s](hero-collage/entrance-11000.png) |

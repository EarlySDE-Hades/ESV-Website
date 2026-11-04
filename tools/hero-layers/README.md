# Hero layer tooling

This is offline artwork tooling. The website has no build step or runtime packages.
Use Python 3.14 (tested on Windows), install `requirements.txt` in a virtual environment,
and retain the ignored original `Brand Assets/New v2.png` locally.

```powershell
python -m venv tools/hero-layers/.venv
tools/hero-layers/.venv/Scripts/python -m pip install -r tools/hero-layers/requirements.txt
# Regenerate every served asset, manifest and audit with one command:
tools/hero-layers/.venv/Scripts/python tools/hero-layers/generate.py
```

On macOS/Linux use `.venv/bin/python` in place of `.venv/Scripts/python`.

`masks.json` stores source-coordinate contours and holes. The generator refines narrow
contour bands with deterministic OpenCV GraphCut, separates plant colors, keys the
known #F4F4F4 matte, and un-premultiplies the one-pixel outer antialiasing band.
People's opaque pixels are copied directly and encoded losslessly; there is no AI,
retouching, warping or face animation. Architecture and plant use quality-90 WebP.
Half-size exports use quality 95. Transparent pixels are cleared before encoding.

Hidden architectural regions use source facade repeats and OpenCV Telea inpainting.
Only occluded pixels receive fill; visible architecture is restored from the source.
The SVG sun and sparkles use sampled colors and source coordinates. Unlike the brief's
inventory, the original sun contains grain and the sparkles have eight separate rays.
SVG rebuilding approximates those small photographic details.

`assets/hero/manifest.json` records cropped bounds (including four-pixel padding),
z-order, SVG geometry, byte counts and a source SHA-256. Positioning is embedded in
HTML by `markup.py` at the end of generation; the browser never fetches the manifest.
Regenerating for a different source requires reviewing the contours and the result.

Generated review output is ignored in `out/`: individual masks and layers,
`recomposite.png`, an 8x-amplified `diff.png`, and `metrics.json`. The audit reads back
the actual exported desktop WebPs. MAE is measured over the entire RGB canvas;
connected differences above 16 channel levels are also reported so a small mean
cannot conceal a local defect. Lossless opaque people RGB is checked separately.

Use `http://127.0.0.1:5173/?slow=10` for a ten-times slower entrance inspection.
See `docs/hero-collage-report.md` for the acceptance results and any remaining limits.

For the repeatable browser audit, run the static server from the repo root, install
the development-only browser driver, then run the audit (Google Chrome must be installed):

```powershell
npm.cmd install --prefix tools/hero-layers --no-save --package-lock=false playwright@1.56.1
node tools/hero-layers/verify.mjs
```

The audit writes viewport/entrance screenshots to `docs/hero-collage/` and detailed
results to `out/browser-report.json`. It covers load failure, decode timeout,
visibility gating, pointer interruption, scroll return, occasional twinkle,
initial/runtime reduced motion, no-JS, overflow, compositor-hint cleanup and CLS.
Tab-hidden cancellation is simulated because headless Chrome does not reliably
background tabs; hardware frame pacing still requires a representative laptop.

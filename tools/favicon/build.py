"""Build the favicon set from the unicorn-seedling brandmark, on a transparent background.

    python tools/favicon/build.py

The source (favicon source.png, gitignored) is a fine line on transparency (~8px stroke
at ~1400px tall), which would vanish at tab sizes. For each output size the stroke is
thickened to a target *rendered* width, then the mark is scaled to fit the square.

- favicon.svg: ink switches to white under prefers-color-scheme: dark, so the mark
  stays visible on dark browser tabs. Chrome, Edge and Firefox use this one.
- favicon.ico / PNGs: black ink on transparency (Safari and older browsers).
- apple-touch-icon keeps a fair tile: iOS fills transparency with black, which would
  hide black ink.
"""
from base64 import b64encode
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "favicon source.png"
ICONS = ROOT / "assets" / "brand" / "icons"
FAIR, INK, WHITE = (244, 244, 244), (17, 17, 17), (244, 244, 244)
SRC_STROKE = 8.0           # measured stroke width in the source, px

a = np.asarray(Image.open(SRC).convert("RGBA").getchannel("A"), dtype=np.float32) / 255


def to_mask(arr):
    m = Image.fromarray((arr * 255).astype(np.uint8))
    return m.crop(m.point(lambda v: 255 if v > 40 else 0).getbbox())


# Tab sizes keep only the single continuous line: the separate eye arc and nostril
# dot clog into a smudge below ~64px.
labels, n = ndimage.label(a > 0.5)
largest = 1 + int(np.argmax(ndimage.sum(np.ones_like(labels), labels, range(1, n + 1))))
keep = ndimage.binary_dilation(labels == largest, iterations=3)
MASKS = {"full": to_mask(a), "simple": to_mask(a * keep)}


def icon(size, fill, stroke_px, ink=INK, tile=False, simple=None):
    """fill: share of the square the mark's longer side takes; stroke_px: rendered stroke."""
    mask = MASKS["simple" if (size <= 48 if simple is None else simple) else "full"]
    S = size * 8                                       # supersample
    scale = S * fill / max(mask.size)
    want_src = (stroke_px * 8) / scale                 # thicken so stroke * scale == stroke_px * 8
    grow = max(0, round(want_src - SRC_STROKE))
    m = mask
    if grow >= 2:
        k = grow + (1 - grow % 2)                      # odd kernel
        m = Image.new("L", (mask.width + 2 * k, mask.height + 2 * k), 0)
        m.paste(mask, (k, k))
        m = m.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.GaussianBlur(1.2))
        m = m.crop(m.point(lambda v: 255 if v > 40 else 0).getbbox())
    r = S * fill / max(m.size)
    m = m.resize((max(1, round(m.width * r)), max(1, round(m.height * r))), Image.Resampling.LANCZOS)

    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if tile:
        ImageDraw.Draw(out).rectangle((0, 0, S, S), fill=FAIR + (255,))
    layer = Image.new("RGBA", m.size, ink + (255,))
    layer.putalpha(m)
    out.alpha_composite(layer, ((S - m.width) // 2, (S - m.height) // 2))
    return out.resize((size, size), Image.Resampling.LANCZOS)


def png_b64(im):
    buf = BytesIO()
    im.save(buf, "PNG", optimize=True)
    return b64encode(buf.getvalue()).decode()


if __name__ == "__main__":
    ICONS.mkdir(parents=True, exist_ok=True)
    i16, i32, i48 = icon(16, 1.0, 1.25), icon(32, 0.98, 1.6), icon(48, 0.96, 2.0)
    i48.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[i16, i32])
    i16.save(ICONS / "favicon-16.png")
    i32.save(ICONS / "favicon-32.png")
    icon(180, 0.72, 4.2, tile=True).convert("RGB").save(ICONS / "apple-touch-icon.png")
    icon(192, 0.86, 4.4).save(ICONS / "icon-192.png")
    icon(512, 0.86, 10).save(ICONS / "icon-512.png")

    # Light/dark-aware SVG wrapping a 64px raster drawn for tab sizes
    light, dark = png_b64(icon(64, 0.98, 3.0, simple=True)), png_b64(icon(64, 0.98, 3.0, ink=WHITE, simple=True))
    (ROOT / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<style>.d{display:none}@media (prefers-color-scheme:dark){.l{display:none}.d{display:inline}}</style>'
        f'<image class="l" width="64" height="64" href="data:image/png;base64,{light}"/>'
        f'<image class="d" width="64" height="64" href="data:image/png;base64,{dark}"/>'
        '</svg>', encoding="utf-8")
    print("favicon set written")

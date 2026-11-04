"""Build the favicon set from the unicorn-seedling line drawing.

    python tools/favicon/build.py

The source is fine line art (~10px stroke at 1254px), which would vanish at tab sizes.
The drawing's ink is extracted, then for each output size the stroke is thickened to a
target *rendered* width and the drawing is placed on a clean fair (#F4F4F4) tile.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Brand Assets" / "favicon-unicorn-seedling.png"
ICONS = ROOT / "assets" / "brand" / "icons"
FAIR, INK = (244, 244, 244), (17, 17, 17)
SRC_STROKE = 10.0          # measured stroke width in the source, px

# Ink mask (anti-aliased) cropped to the drawing
g = np.asarray(Image.open(SRC).convert("L"), dtype=np.float32)
alpha = np.clip((236 - g) / (236 - 40), 0, 1)
alpha[g > 236] = 0

def to_mask(a):
    m = Image.fromarray((a * 255).astype(np.uint8))
    return m.crop(m.point(lambda v: 255 if v > 40 else 0).getbbox())


# Tab sizes keep only the single continuous line (outline, horn, stem, leaf, smile):
# the separate eye arc and nostril dot clog into a smudge below ~64px.
labels, n = ndimage.label(g < 150)
largest = 1 + int(np.argmax(ndimage.sum(np.ones_like(labels), labels, range(1, n + 1))))
keep = ndimage.binary_dilation(labels == largest, iterations=3)
MASKS = {"full": to_mask(alpha), "simple": to_mask(alpha * keep)}


def icon(size, fill, stroke_px, rounded=True, radius=0.22):
    mask = MASKS["simple" if size <= 48 else "full"]
    """fill: drawing height as a fraction of the tile; stroke_px: rendered stroke width."""
    S = size * 8                                       # supersample
    content_h = S * fill
    scale = content_h / mask.height
    # Thicken in source space so that stroke * scale == stroke_px * 8
    want_src = (stroke_px * 8) / scale
    grow = max(0, round(want_src - SRC_STROKE))
    m = mask
    if grow >= 2:
        k = grow + (1 - grow % 2)                      # odd kernel
        pad = k
        m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
        m.paste(mask, (pad, pad))
        m = m.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.GaussianBlur(1.2))
        m = m.crop(m.point(lambda v: 255 if v > 40 else 0).getbbox())
    w = round(m.width * content_h / m.height)
    m = m.resize((w, round(content_h)), Image.Resampling.LANCZOS)

    tile = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    if rounded:
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * radius), fill=FAIR + (255,))
    else:
        d.rectangle((0, 0, S, S), fill=FAIR + (255,))
    ink = Image.new("RGBA", m.size, INK + (255,))
    ink.putalpha(m)
    tile.alpha_composite(ink, ((S - m.width) // 2, (S - m.height) // 2))
    return tile.resize((size, size), Image.Resampling.LANCZOS)


if __name__ == "__main__":
    ICONS.mkdir(parents=True, exist_ok=True)
    i16, i32, i48 = icon(16, 0.86, 1.15, radius=0.2), icon(32, 0.82, 1.45), icon(48, 0.78, 1.9)
    i48.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[i16, i32])
    i16.save(ICONS / "favicon-16.png")
    i32.save(ICONS / "favicon-32.png")
    icon(180, 0.66, 4.2, rounded=False).convert("RGB").save(ICONS / "apple-touch-icon.png")  # iOS masks it
    icon(192, 0.66, 4.4).save(ICONS / "icon-192.png")
    icon(512, 0.66, 10).save(ICONS / "icon-512.png")
    print("favicon set written")

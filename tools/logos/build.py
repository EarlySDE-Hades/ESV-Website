"""Build web-ready logo assets and markup from the (gitignored) Logos/ source folder.

    python tools/logos/build.py

- Rasters are cropped to their visible pixels, downscaled (never upscaled) to 2x their
  display size, and saved as WebP with alpha. SVGs are copied untouched.
- Logos are balanced by *visual area*, not equal height, so square marks don't dwarf
  wide wordmarks: display size ~ sqrt(area / aspect), capped by a max width and height.
- Prints the <li> markup for the campus, portfolio and team logos.
"""
from html import escape
from collections import deque
from math import sqrt
from pathlib import Path
import re
import shutil

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Logos"
OUT = ROOT / "assets" / "logos"

# (source file, output slug, alt text, caption). Caption None = no sector shown.
PORTFOLIO = [
    ("Companies/FWDA logo.png", "flying-wedge", "Flying Wedge Defence & Aerospace", "Defence &amp; Aerospace"),
    ("Companies/Skyroot.svg", "skyroot", "Skyroot Aerospace", "Space-tech"),
    ("Companies/Garuda Aerospace.webp", "garuda-aerospace", "Garuda Aerospace", "Drone-tech"),
    ("Companies/Hesa.png", "hesa", "Hesa", "Rural Commerce Platform"),
    ("Companies/Electriq.png", "electriq", "Electriq", "Electric Mobility"),
    ("Companies/kyoora.png", "kyoora", "Kyoora", None),
    ("Companies/Artment.png", "artment", "Artment", None),
    ("Companies/alchemyst AI.svg", "alchemyst-ai", "Alchemyst AI", None),
    ("Companies/EsportsXO.webp", "esportsxo", "EsportsXO", None),
    ("Companies/OLL.png", "oll", "OLL", None),
]
CAMPUS = [
    ("Partners/NMIMS.png", "nmims", "SVKM's NMIMS"),
    ("Partners/Manipal.png", "manipal", "Manipal Academy of Higher Education"),
    ("Partners/MIT WPU.png", "mit-wpu", "MIT World Peace University, Pune"),
    ("Partners/WISE - SNDTWU.PNG", "wise-sndtwu", "WISE, SNDTWU Incubation Centre"),
    ("Partners/RCOEM.png", "rcoem", "Shri Ramdeobaba College of Engineering and Management, Nagpur"),
    ("Partners/maharashtra state innovation society.png", "msins", "Maharashtra State Innovation Society"),
]
TEAM = [
    ("Team/Ascent.jpg", "ascent", "Ascent"),
    ("Team/bluearc_advisors_llp_logo.jpg", "bluearc", "BlueArc Advisors"),
    ("Team/bni-2020-logo-png_seeklogo-378515.png", "bni", "BNI"),
    ("Team/Corporate Connections.jpg", "corporate-connections", "Corporate Connections"),
    ("Team/mnco_logo.jpg", "mn-co", "MN & Co. Chartered Accountants"),
    ("Team/New-logo-of-CA.png", "ca-india", "CA India"),
    ("Team/Yaha Waters.jpg", "yaha-water", "Yaha Water Systems"),
    ("Team/cropped-FINAL-LOGO.png", "vis-legis", "Vis Legis Law Practice"),
    ("Team/RotaryMBS-Simple_RGB.png", "rotary", "Rotary"),
    ("Team/WILL_logo_negativo_340.png", "will", "Worldwide Independent Lawyers League"),
]

# Display boxes in CSS px (assets are exported at 2x these)
BOXES = {
    "portfolio": dict(area=9000, max_w=176, max_h=78),
    "campus": dict(area=7600, max_w=168, max_h=72),
    "team": dict(area=2400, max_w=120, max_h=28),
}


def remove_white_background(im, protected_box=None):
    """Remove only edge-connected white, preserving enclosed white details."""
    w, h = im.size
    pixels = im.load()
    background = Image.new("L", im.size)
    mask = background.load()
    protected = Image.new("L", im.size)
    if protected_box:
        protected.paste(255, protected_box)
    keep = protected.load()
    queue = deque()

    def visit(x, y):
        if not mask[x, y] and not keep[x, y] and min(pixels[x, y][:3]) >= 245:
            mask[x, y] = 255
            queue.append((x, y))

    for x in range(w):
        visit(x, 0)
        visit(x, h - 1)
    for y in range(h):
        visit(0, y)
        visit(w - 1, y)
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h:
                visit(nx, ny)

    # Two source pixels cover antialiasing and JPEG ringing next to the flood.
    # Do not apply this globally: white counters and BNI's details must survive.
    edge = background.filter(ImageFilter.MaxFilter(5)).load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if mask[x, y]:
                pixels[x, y] = (0, 0, 0, 0)
            elif edge[x, y] and not keep[x, y] and min(r, g, b) < 245:
                alpha = max(255 - r, 255 - g, 255 - b) / 255
                if alpha:
                    rgb = tuple(round(255 - (255 - c) / alpha) for c in (r, g, b))
                    pixels[x, y] = (*rgb, round(a * alpha))
                else:
                    pixels[x, y] = (0, 0, 0, 0)
    return im


def prepare_team(im, slug):
    if slug == "will":
        # The supplied negative PNG already has a transparent background; its
        # cream pixels are lettering, not a matte. Preserve the existing alpha.
        # A positive version should replace this when one is available.
        navy = Image.new("RGBA", im.size, "#1B2A4A")
        navy.putalpha(im.getchannel("A"))
        return navy
    if slug in {"vis-legis", "rotary"}:
        return im
    if slug == "bni":
        # The white diagonal separating the i's dot touches the exterior. Protect
        # that letter's source bounds as well as the automatically enclosed whites.
        return remove_white_background(im, protected_box=(470, 196, 533, 403))
    if slug == "yaha-water":
        # The side frame (including its JPEG fringe) occupies 16px on each side;
        # all artwork is inside these bounds. Remove it before the white flood.
        im = im.crop((16, 0, im.width - 16, im.height))
        # Its light-grey matte has JPEG noise below the white threshold. Normalize
        # only these near-neutral highlights, then let the edge flood decide
        # which are background (the white lettering stays enclosed and intact).
        pixels = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = pixels[x, y]
                if min(r, g, b) >= 235 and max(r, g, b) - min(r, g, b) <= 12:
                    pixels[x, y] = (255, 255, 255, a)
    return remove_white_background(im)


def display_size(w, h, box):
    ratio = w / h
    dh = sqrt(box["area"] / ratio)
    dw = dh * ratio
    scale = min(1, box["max_w"] / dw, box["max_h"] / dh)
    return round(dw * scale), round(dh * scale)


def svg_aspect(path):
    m = re.search(r'viewBox="([\d.\s-]+)"', path.read_text(encoding="utf-8"))
    _, _, w, h = map(float, m.group(1).split())
    return w, h


def build(src_rel, slug, group):
    src = SRC / src_rel
    box = BOXES[group]
    if group == "team" and slug in {"ascent", "corporate-connections", "ca-india", "yaha-water"}:
        box = dict(box, max_h=40)
    dest_dir = OUT / group
    dest_dir.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".svg":
        w, h = svg_aspect(src)
        dest = dest_dir / f"{slug}.svg"
        shutil.copyfile(src, dest)
        return dest, display_size(w, h, box), None
    im = Image.open(src).convert("RGBA")
    if group == "team":
        im = prepare_team(im, slug)
    bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    im = im.crop(bbox)
    dw, dh = display_size(im.width, im.height, box)
    target = (dw * 2, dh * 2)
    soft = im.width < target[0] * 0.75   # source too small for crisp 2x
    if group == "team":
        # Keep every native pixel in the two tiny wordmarks. All other exports
        # fit a 2x display box, with a transparent 1px guard against edge clipping.
        if slug not in {"bluearc", "mn-co"}:
            im.thumbnail((target[0] - 2, target[1] - 2), Image.Resampling.LANCZOS)
        im = ImageOps.expand(im, border=1, fill=(0, 0, 0, 0))
        if slug == "will":
            # Resampling premultiplied alpha can round RGB; restore exact navy.
            alpha = im.getchannel("A")
            im = Image.new("RGBA", im.size, "#1B2A4A")
            im.putalpha(alpha)
    elif im.width > target[0]:
        im = im.resize(target, Image.Resampling.LANCZOS)
    dest = dest_dir / f"{slug}.webp"
    # Lossless keeps WILL exactly navy; all other logos use quality 90.
    im.save(dest, quality=90, method=6, lossless=(group == "team" and slug == "will"))
    return dest, (dw, dh), soft


def img_tag(dest, size, alt):
    rel = dest.relative_to(ROOT).as_posix()
    w, h = size
    return (f'<img src="{rel}" alt="{escape(alt)}" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async" draggable="false" />')


if __name__ == "__main__":
    print("<!-- campus -->")
    for src, slug, alt in CAMPUS:
        dest, size, soft = build(src, slug, "campus")
        print(f"          <li>{img_tag(dest, size, alt)}</li>")
        if soft: print(f"<!-- NOTE: {src} is low-resolution -->")
    print("<!-- portfolio -->")
    for src, slug, alt, caption in PORTFOLIO:
        dest, size, soft = build(src, slug, "portfolio")
        # Sector, summary and posts live in the #portfolio-data JSON in index.html
        print(f'          <li class="company"><button class="company__mark" type="button" '
              f'aria-haspopup="dialog" data-company="{slug}">{img_tag(dest, size, alt)}</button></li>')
        if soft: print(f"<!-- NOTE: {src} is low-resolution -->")
    print("<!-- team -->")
    for src, slug, alt in TEAM:
        dest, size, soft = build(src, slug, "team")
        print(f"              <li>{img_tag(dest, size, alt)}</li>")
        if soft: print(f"<!-- NOTE: {src} is low-resolution -->")
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"<!-- total logo bytes: {total} -->")

"""Build web-ready logo assets and markup from the (gitignored) Logos/ source folder.

    python tools/logos/build.py

- Rasters are cropped to their visible pixels, downscaled (never upscaled) to 2x their
  display size, and saved as WebP with alpha. SVGs are copied untouched.
- Logos are balanced by *visual area*, not equal height, so square marks don't dwarf
  wide wordmarks: display size ~ sqrt(area / aspect), capped by a max width and height.
- Prints the <li> markup for the campus row and portfolio strip, to paste into index.html.
"""
from html import escape
from math import sqrt
from pathlib import Path
import re
import shutil

from PIL import Image

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

# Display boxes in CSS px (assets are exported at 2x these)
BOXES = {
    "portfolio": dict(area=9000, max_w=176, max_h=78),
    "campus": dict(area=7600, max_w=168, max_h=72),
}


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
    dest_dir = OUT / group
    dest_dir.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".svg":
        w, h = svg_aspect(src)
        dest = dest_dir / f"{slug}.svg"
        shutil.copyfile(src, dest)
        return dest, display_size(w, h, box), None
    im = Image.open(src).convert("RGBA")
    bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    im = im.crop(bbox)
    dw, dh = display_size(im.width, im.height, box)
    target = (dw * 2, dh * 2)
    soft = im.width < target[0] * 0.75   # source too small for crisp 2x
    if im.width > target[0]:
        im = im.resize(target, Image.Resampling.LANCZOS)
    dest = dest_dir / f"{slug}.webp"
    im.save(dest, quality=90, method=6)
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
        cap = (f'<span class="company__sector">{caption}</span>' if caption
               else '<span class="company__sector" aria-hidden="true">&nbsp;</span>')
        print(f'          <li class="company"><span class="company__mark">{img_tag(dest, size, alt)}</span>{cap}</li>')
        if soft: print(f"<!-- NOTE: {src} is low-resolution -->")
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"<!-- total logo bytes: {total} -->")

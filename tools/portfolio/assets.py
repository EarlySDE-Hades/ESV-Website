"""Logos and founder photos for the company pages. Run after adding a source file, then run tools/team/build.py.

    python tools/portfolio/assets.py

- Logos: Logos/Companies/profile/<slug>.png|svg (gitignored), or the file named in LOGOS.
  Trimmed to the visible mark and sized so each one looks the same size on its white plate
  (equal visual area, not equal height). Output: assets/logos/profile/ + tools/portfolio/logos.json.
- Founder photos: Founder Photos/companies/<slug>/<name-in-lowercase-with-dashes>.png|jpg|webp (gitignored).
  Kept whole; the square card shows a tall photo from the top, so a head is never cut. Output: assets/portfolio/founders/<slug>-<name>.webp + tools/portfolio/photos.json.
"""
import json
import sys
from math import sqrt
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools/logos"))
from build import remove_white_background  # noqa: E402

SRC = ROOT / "Logos/Companies"
OUT = ROOT / "assets/logos/profile"
LOGOS = {"alchemyst-ai": "alchemyst AI.svg", "artment": "Artment.png", "electriq": "Electriq.png", "flying-wedge": "FWDA logo.png",
         "garuda-aerospace": "Garuda Aerospace.webp", "hesa": "Hesa-wordmark", "kyoora": "kyoora.png", "oll": "OLL.png", "skyroot": "Skyroot.svg"}
WHITE = {"esportsxo", "shaurrya-teleservices"}      # sources on a white background
CROP = {"misfits": (0.1, 0.359, 0.9, 0.69)}        # the mark inside a larger sheet (share of width and height)
AREA, MAX_W, MAX_H = 9200, 200, 92                  # the plate is 256 x 136 CSS px


def load(slug):
    if slug in ("hesa", "alchemyst-ai", "skyroot"):  # SVGs already prepared for the home page
        p = ROOT / f"assets/logos/portfolio/{slug}.svg"
        pg = fitz.open(p)[0]
        pix = pg.get_pixmap(matrix=fitz.Matrix(1400 / pg.rect.width, 1400 / pg.rect.width), alpha=True)
        return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    own = next(iter(sorted((SRC / "profile").glob(f"{slug}.*"))), None)
    p = own or (SRC / LOGOS[slug] if slug in LOGOS else None)
    return Image.open(p).convert("RGBA") if p and p.exists() else None


def logos(slugs):
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for slug in slugs:
        im = load(slug)
        if im is None:
            print("no logo:", slug)
            continue
        if slug in CROP:
            w, h = im.size
            l, t, r, b = CROP[slug]
            im = im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
        if slug in WHITE:
            im = remove_white_background(im)
        im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox())
        # Equal visual area: a solid mark needs less room than a thin, airy one of the same box.
        ink = sum(im.getchannel("A").resize((100, 100)).get_flattened_data()) / 255 / 10000
        area = AREA * (0.45 / max(0.2, min(0.8, ink))) ** 0.3
        ratio = im.width / im.height
        dh = sqrt(area / ratio)
        k = min(1, MAX_W / (dh * ratio), MAX_H / dh)
        w, h = round(dh * ratio * k), round(dh * k)
        soft = im.width < w * 1.5
        if im.width > w * 3:
            im = im.resize((w * 3, h * 3), Image.Resampling.LANCZOS)
        im.save(OUT / f"{slug}.webp", quality=92, method=6)
        out[slug] = [w, h]
        print(f"{slug:24} {w}x{h} ink {ink:.2f}", "LOW RESOLUTION" if soft else "")
    (HERE / "logos.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")


def photos():
    dest = ROOT / "assets/portfolio/founders"
    dest.mkdir(parents=True, exist_ok=True)
    out = {}
    for f in sorted((ROOT / "Founder Photos/companies").glob("*/*.*")):
        im = Image.open(f)
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")   # a cut-out keeps its transparency
        im.thumbnail((640, 800), Image.Resampling.LANCZOS)
        name = f"{f.parent.name}-{f.stem}"
        im.save(dest / f"{name}.webp", quality=84, method=6)
        out[name] = list(im.size)
        print(name, im.size)
    (HERE / "photos.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    logos([c["slug"] for c in json.loads((HERE / "companies.json").read_text(encoding="utf-8"))["companies"]])
    photos()

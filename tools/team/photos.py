"""Build the team portraits from the HD cut-outs in Founder Photos/ (gitignored).

    python tools/team/photos.py

Each cut-out is transparent. We find the head in its alpha silhouette (top of the hair
down to the narrowest point of the neck), then scale and crop a square so every head
fills the same share of the frame, and composite it on the brand beige.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Founder Photos"
OUT = ROOT / "assets" / "team"
BEIGE = (211, 193, 169)          # --sand
SIZE = 600                       # exported square (displayed at up to ~280px, ~2x)
HEAD = 0.50                      # head height (crown to neck) as a share of the frame
TOP = 0.13                       # space above the crown

PEOPLE = [
    ("MG's Pic_nobg.png", "monica-gupta"),
    ("Manan_nobg.png", "manan-patel"),
    ("Nimit Shah Photo New Nobg.png", "nimit-shah"),
    ("Rahul_new_nobg.png", "rahul-hingmire"),
    ("Sudhir_nobg.png", "sudhir-mehta"),
]
# Fine-tuning per person if the silhouette misreads (hair volume etc.): scale multiplier, x/y nudge (share of frame)
TUNE = {"rahul-hingmire": (0.92, 0.0, 0.0)}
# Where the chin/neck sits, as a share of the height below the crown, when the silhouette can't show it
NECK = {"monica-gupta": 0.31}


def head_box(im, slug):
    a = im.getchannel("A")
    w, h = a.size
    scale = 600 / h                                  # measure on a small copy
    small = a.resize((max(1, int(w * scale)), 600))
    sw, sh = small.size
    px = small.load()
    rows = []
    for y in range(sh):
        xs = [x for x in range(sw) if px[x, y] > 128]
        rows.append((xs[0], xs[-1]) if xs else None)
    top = next(y for y, r in enumerate(rows) if r and r[1] - r[0] > sw * 0.04)   # skip stray specks above the crown
    # Walk down from the crown: the head widens, the neck narrows (a dip below the head's
    # width), then the shoulders jump out. Neck = the narrowest row of that dip.
    span = lambda r: (r[1] - r[0]) if r else 0
    head_max, neck, neck_span, in_dip = 0, None, None, False
    for y in range(top, sh):
        sp = span(rows[y])
        if not in_dip:
            head_max = max(head_max, sp)
            if head_max and y - top > head_max * 0.9 and sp < head_max * 0.85:   # a neck sits at least a head-width down
                in_dip, neck, neck_span = True, y, sp
        else:
            if sp < neck_span:
                neck, neck_span = y, sp
            if sp > neck_span * 1.3:
                break
    if neck is None or slug in NECK:                  # long hair can hide the neck: use the measured share instead
        neck = top + (sh - top) * NECK.get(slug, 0.5)
    cx_row = rows[top + int((neck - top) * 0.55)]
    return top / scale, neck / scale, (sum(cx_row) / 2) / scale


def build(src, slug):
    im = Image.open(SRC / src).convert("RGBA")
    top, neck, cx = head_box(im, slug)
    k, dx, dy = TUNE.get(slug, (1.0, 0.0, 0.0))
    head_h = (neck - top) / k
    s = (SIZE * HEAD) / head_h                        # px per source px
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    top, cx = top * s, cx * s
    left = cx - SIZE / 2 - dx * SIZE
    upper = top - SIZE * TOP - dy * SIZE
    canvas = Image.new("RGBA", (SIZE, SIZE), BEIGE + (255,))
    canvas.paste(im, (round(-left), round(-upper)), im)
    canvas.convert("RGB").save(OUT / f"{slug}.webp", quality=88, method=6)
    print(slug, f"head {neck - top:.0f}px", f"scale {s:.3f}")


if __name__ == "__main__":
    for src, slug in PEOPLE:
        build(src, slug)

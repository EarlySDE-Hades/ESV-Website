"""Drawn art for Perspectives articles, in ESV colours: a wide header for the article and a book cover for the shelf.

Each article names its art in posts.json ("art": "house"). The same drawing appears in both places.
Colours come from --sx-* on .post-page and .cover in css/styles.css (a pale sand, b sand, c golden glow, d purple, e bronze).
Every drawing sits in a 400 x 300 box, standing on y = 300.
"""
A, B, C, D, E = (f'fill="var(--sx-{k})"' for k in "abcde")
W = 'fill="#fff"'
P = 'fill="var(--pastel-purple)"'


def _line(d, w=3, col="c", o=1, dash=""):
    dash = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="var(--sx-{col})" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{o}"{dash}/>'


def house():
    """Part 1: a house split into shares, one block for each owner."""
    s = f'<path d="M80 140 200 50l120 90z" {C}/><rect x="262" y="66" width="22" height="46" {E}/>'
    s += f'<rect x="96" y="138" width="208" height="162" {W} stroke="var(--sx-b)" stroke-width="2"/>'
    cols = [E, E, C, C, B, B, A, A, D, D]   # four friends in warm tones (2 columns, 20% each), Esha in purple
    for i in range(10):
        for j in range(6):
            s += f'<rect x="{104 + i * 19.6:.1f}" y="{148 + j * 24}" width="16" height="20" rx="3" {cols[i]}/>'
    s += f'<rect x="178" y="236" width="44" height="64" rx="4" {W} stroke="var(--sx-c)" stroke-width="4"/>'
    s += f'<g transform="translate(346 236)"><ellipse cx="0" cy="54" rx="34" ry="10" {E}/><rect x="-34" y="20" width="68" height="34" {E}/><ellipse cx="0" cy="20" rx="34" ry="10" {C}/><text x="0" y="27" text-anchor="middle" font-family="Inter, sans-serif" font-weight="700" font-size="20" fill="#fff">₹</text></g>'
    return s + _line("M30 300h340", 4)


def paper():
    """Part 2: the same money, different paper."""
    s = f'<g transform="rotate(-8 130 190)"><rect x="40" y="80" width="170" height="210" rx="8" {B}/>' + "".join(_line(f"M64 {y}h120", 6, "a") for y in (130, 156, 182, 208)) + "</g>"
    s += f'<g transform="rotate(6 270 190)"><rect x="190" y="70" width="170" height="214" rx="8" {E}/>' + "".join(_line(f"M214 {y}h{w}", 6, "a") for y, w in ((112, 120), (138, 96), (164, 120))) + "</g>"
    s += f'<rect x="110" y="60" width="180" height="234" rx="10" {W} stroke="var(--sx-c)" stroke-width="4"/>'
    s += f'<text x="200" y="104" text-anchor="middle" font-family="Sorts Mill Goudy, Georgia, serif" font-size="22" fill="var(--sx-c)">Share</text><text x="200" y="128" text-anchor="middle" font-family="Sorts Mill Goudy, Georgia, serif" font-size="22" fill="var(--sx-c)">Certificate</text>'
    s += "".join(_line(f"M142 {y}h116", 5, "b") for y in (156, 178, 200))
    s += f'<circle cx="244" cy="250" r="26" {D}/><circle cx="244" cy="250" r="16" fill="none" stroke="#fff" stroke-width="3"/><path d="M230 272l-8 26 14-8 8 12 2-26zM258 272l8 26-14-8-8 12-2-26z" {D}/>'
    for k in range(4):
        s += f'<ellipse cx="66" cy="{290 - k * 14}" rx="34" ry="10" {C if k % 2 else E}/>'
    return s + _line("M20 300h360", 4)


def esop():
    """Part 3: options earned step by step, with a one-year cliff."""
    s = "".join(f'<rect x="{60 + i * 74}" y="{300 - h}" width="60" height="{h}" rx="6" {f}/>' for i, (h, f) in enumerate(((40, B), (90, E), (140, C), (190, C))))
    s = f'<rect x="50" y="270" width="300" height="30" rx="6" {A}/>' + s
    for i in range(4):
        for k in range(i + 1):
            s += f'<circle cx="{90 + i * 74}" cy="{300 - (40, 90, 140, 190)[i] - 16 - k * 26}" r="10" {D if k == i else P}/>'
    s += _line("M66 260V150", 4, "c") + f'<path d="M68 150h40l-9 13 9 13H68z" {C}/>'
    s += f'<g transform="translate(340 46) scale(.8)"><circle r="22" fill="none" stroke="var(--sx-c)" stroke-width="7"/><path d="M16 14l40 40M44 42l10-10M52 50l10-10" fill="none" stroke="var(--sx-c)" stroke-width="7" stroke-linecap="round"/></g>'
    return s + _line("M30 300h340", 4)


def pie():
    """Part 4: a new investor takes a slice, and the whole grows."""
    import math
    cx, cy, r = 170, 170, 112
    slices = [(0.556, E), (0.111, B), (0.167, C), (0.166, D)]
    a, s = -90, ""
    for k, (f, fill) in enumerate(slices):
        b = a + f * 360
        off = 16 if k == 3 else 0
        mid = math.radians((a + b) / 2)
        ox, oy = off * math.cos(mid), off * math.sin(mid)
        x1, y1 = cx + ox + r * math.cos(math.radians(a)), cy + oy + r * math.sin(math.radians(a))
        x2, y2 = cx + ox + r * math.cos(math.radians(b)), cy + oy + r * math.sin(math.radians(b))
        s += f'<path d="M{cx + ox:.1f} {cy + oy:.1f}L{x1:.1f} {y1:.1f}A{r} {r} 0 {1 if b - a > 180 else 0} 1 {x2:.1f} {y2:.1f}z" {fill} stroke="#fff" stroke-width="4"/>'
        a = b
    s += f'<g transform="translate(340 160)"><rect x="-14" y="0" width="28" height="100" rx="5" {C}/><path d="M-36 6 0-40 36 6z" {C}/></g>'
    return s + _line("M30 300h340", 4)


def village():
    """Hesa: a village, its fields, and the phone that connects it."""
    s = f'<path d="M0 300c60-40 140-50 220-40s130 0 180-20v60z" {A}/>'
    for x, w, h in ((40, 90, 70), (150, 70, 56)):
        s += f'<rect x="{x}" y="{300 - h}" width="{w}" height="{h}" {W}/><path d="M{x - 10} {300 - h}l{w / 2 + 10} -{h * .6:.0f}l{w / 2 + 10} {h * .6:.0f}z" {C}/><rect x="{x + w / 2 - 10}" y="{300 - h * .55:.0f}" width="20" height="{h * .55:.0f}" {E}/>'
    s += f'<path d="M230 300l20-40h120l30 40z" {B}/>' + "".join(_line(f"M{254 + k * 26} 300 {262 + k * 22} 262", 3, "a") for k in range(5))
    s += f'<g transform="translate(330 60)"><rect x="-40" y="0" width="80" height="150" rx="14" fill="var(--sx-d)"/><rect x="-32" y="14" width="64" height="112" rx="6" {W}/><path d="M0 34c-12 0-20 8-20 20 0 14 20 34 20 34s20-20 20-34c0-12-8-20-20-20z" {C}/><circle cy="54" r="7" {W}/><circle cy="138" r="5" {W}/></g>'
    s += _line("M200 170c30-50 60-70 90-84", 3, "d", 1, "2 9")
    return s + _line("M0 300h400", 4)


def classroom():
    """OLL: skills that school leaves out."""
    s = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" {f}/>' for x, y, w, h, f in ((60, 260, 200, 40, E), (76, 222, 170, 38, B), (54, 188, 210, 34, C)))
    s += f'<path d="M160 120l104 36-104 36-104-36z" fill="var(--sx-d)"/><path d="M104 172v22c32 18 80 18 112 0v-22l-56 20z" {P}/>' + _line("M264 156v50", 4, "d") + f'<circle cx="264" cy="212" r="8" fill="var(--sx-d)"/>'
    s += f'<g transform="translate(330 150)"><circle r="40" {W} stroke="var(--sx-c)" stroke-width="5"/>' + "".join(f'<rect x="-6" y="-56" width="12" height="18" rx="3" {C} transform="rotate({a})"/>' for a in range(0, 360, 45)) + f'<circle r="14" {C}/></g>'
    s += f'<path d="M300 80l14-30 14 30-30-18h32z" {D}/>'
    return s + _line("M30 300h340", 4)


DRAW = {"house": house, "paper": paper, "esop": esop, "pie": pie, "village": village, "classroom": classroom}


def _backdrop():
    s = '<circle cx="540" cy="420" r="300" fill="var(--sx-a)"/>'
    s += "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}"/>' for x, y, r, f in ((120, 80, 5, "var(--sx-b)"), (230, 200, 3, "var(--sx-c)"), (900, 70, 6, "var(--sx-b)"), (980, 210, 3, "var(--sx-c)"), (170, 290, 4, "var(--pastel-purple)"), (860, 300, 4, "var(--pastel-purple)")))
    s += _line("M60 330c120-60 200-60 300-20", 2, "b", .8, "2 10") + _line("M740 320c100-50 190-60 290-30", 2, "b", .8, "2 10")
    return s


def header(name):
    """Wide art for the top of an article."""
    return (f'<svg class="post-art__svg" viewBox="0 0 1080 360" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">'
            f'{_backdrop()}<g transform="translate(340 40)">{DRAW[name]()}</g></svg>')


def cover(name):
    """The same drawing on a book cover."""
    return (f'<svg class="cover__art" viewBox="0 70 300 236" preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false">'
            f'<circle cx="150" cy="250" r="120" fill="var(--sx-a)"/><g transform="translate(10 82) scale(0.7)">{DRAW[name]()}</g></svg>')

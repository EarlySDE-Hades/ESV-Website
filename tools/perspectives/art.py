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



def deeptech():
    """Deep Tech, Defined: a lab flask and an atom."""
    s = f'<g transform="translate(150 40)"><path d="M-22 0h44M-14 0v86L-70 214a20 20 0 0 0 18 30h104a20 20 0 0 0 18-30L14 86V0" {W} stroke="var(--sx-c)" stroke-width="5" stroke-linejoin="round"/><path d="M-52 176h104l14 30a14 14 0 0 1-12 20H-50a14 14 0 0 1-12-20z" {P}/>'
    s += "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {W} opacity=".9"/>' for x, y, r in ((-18, 196, 7), (10, 188, 5), (24, 206, 6))) + "</g>"
    s += f'<g transform="translate(300 110)">' + "".join(f'<ellipse rx="62" ry="22" fill="none" stroke="var(--sx-{c})" stroke-width="4" transform="rotate({a})"/>' for a, c in ((0, "c"), (60, "e"), (120, "b"))) + f'<circle r="12" fill="var(--sx-d)"/><circle cx="62" r="6" {C}/><circle cx="-31" cy="54" r="6" {E}/></g>'
    s += f'<rect x="250" y="250" width="110" height="50" rx="6" {B}/><rect x="262" y="262" width="40" height="10" rx="5" {W}/>'
    return s + _line("M30 300h340", 4)


def valley():
    """Where Indian Deep Tech Really Breaks: a bridge with a gap in it."""
    s = f'<path d="M0 300V200h120l20 100zM400 300V160H270l-20 140z" {B}/><path d="M0 200h120M270 160h130" stroke="var(--sx-c)" stroke-width="6"/>'
    s += f'<path d="M120 200c30 10 60 40 78 60" fill="none" stroke="var(--sx-e)" stroke-width="5" stroke-dasharray="3 10" stroke-linecap="round"/><path d="M270 160c-24 14-44 38-58 64" fill="none" stroke="var(--sx-e)" stroke-width="5" stroke-dasharray="3 10" stroke-linecap="round"/>'
    s += "".join(f'<rect x="{x}" y="{y}" width="18" height="{300 - y}" {E}/>' for x, y in ((20, 200), (90, 200), (290, 160), (360, 160)))
    s += f'<g transform="translate(60 170)"><circle r="14" {D}/><path d="M-10 18h20l4 12h-28z" {D}/></g>'
    s += f'<g transform="translate(330 116)"><path d="M0 0v-40" stroke="var(--sx-c)" stroke-width="4"/><path d="M0-40h34l-8 10 8 10H0z" {C}/></g>'
    return s + _line("M0 300h400", 4)


def clipboard():
    """Homework Before the Handshake: a checklist on a clipboard."""
    s = f'<rect x="90" y="40" width="200" height="256" rx="14" {E}/><rect x="104" y="62" width="172" height="222" rx="8" {W}/><rect x="150" y="28" width="80" height="30" rx="8" {C}/>'
    for k in range(5):
        y = 92 + k * 38
        on = k < 3
        s += f'<rect x="122" y="{y}" width="22" height="22" rx="5" fill="{"var(--sx-d)" if on else "none"}" stroke="var(--sx-{"d" if on else "b"})" stroke-width="3"/>'
        if on:
            s += f'<path d="M127 {y + 11}l5 5 9-10" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        s += f'<rect x="156" y="{y + 6}" width="{96 - (k % 2) * 24}" height="10" rx="5" {B if on else A}/>'
    s += f'<g transform="translate(330 220) rotate(-20)"><rect x="-8" y="-70" width="16" height="96" rx="4" {C}/><path d="M-8 26h16l-8 18z" {E}/></g>'
    return s + _line("M40 300h320", 4)


def shield():
    """From Biggest Importer to Builder: a shield, a jet and a gear."""
    s = f'<path d="M180 40l100 36v80c0 70-50 112-100 136-50-24-100-66-100-136V76z" {E}/><path d="M180 66l76 28v62c0 54-38 88-76 106-38-18-76-52-76-106V94z" {W}/>'
    s += f'<path d="M180 108l30 48h-20v50h-20v-50h-20z" fill="var(--sx-d)"/>'
    s += f'<g transform="translate(320 90) rotate(-30) scale(.9)"><path d="M82-10C60-18 30-18 6-16l-52-34h-16l26 36-28 2-16-14h-12l10 20-10 16h12l16-10 28 2-26 38h16l52-36c24 2 54 0 76-4z" {C}/></g>'
    s += f'<g transform="translate(330 250)"><circle r="26" {B}/>' + "".join(f'<rect x="-6" y="-38" width="12" height="16" rx="3" {B} transform="rotate({a})"/>' for a in range(0, 360, 45)) + f'<circle r="10" {W}/></g>'
    return s + _line("M30 300h340", 4)


def clock():
    """Getting Your Fundraising Timing Right: a clock and rising coins."""
    s = f'<circle cx="150" cy="160" r="110" {W} stroke="var(--sx-c)" stroke-width="8"/>' + "".join(f'<rect x="146" y="58" width="8" height="18" rx="4" {B} transform="rotate({a} 150 160)"/>' for a in range(0, 360, 30))
    s += f'<path d="M150 160V96M150 160l46 28" stroke="var(--sx-e)" stroke-width="8" stroke-linecap="round"/><circle cx="150" cy="160" r="10" fill="var(--sx-d)"/>'
    for k in range(4):
        for j in range(k + 2):
            s += f'<ellipse cx="{290 + k * 30}" cy="{290 - j * 12}" rx="14" ry="6" {C if j % 2 else E}/>'
    return s + _line("M30 300h360", 4)


def plate():
    """India Is Eating Itself Sick: a plate, a chips packet and sugar cubes."""
    s = f'<ellipse cx="150" cy="250" rx="120" ry="40" {B}/><ellipse cx="150" cy="242" rx="96" ry="28" {W}/>'
    s += f'<path d="M110 244c10-30 70-30 80 0z" {C}/><circle cx="170" cy="232" r="14" {E}/>'
    s += f'<g transform="translate(300 110) rotate(8)"><path d="M-50 -40h100l-8 20 8 20-8 20 8 20-8 20 8 20H-50l8-20-8-20 8-20-8-20 8-20z" fill="var(--sx-d)"/><rect x="-30" y="-6" width="60" height="30" rx="6" {W}/><circle cy="9" r="8" {C}/></g>'
    s += "".join(f'<rect x="{x}" y="{y}" width="26" height="26" rx="4" {W} stroke="var(--sx-b)" stroke-width="3" transform="rotate({r} {x + 13} {y + 13})"/>' for x, y, r in ((300, 248, 10), (334, 252, -8), (316, 220, 4)))
    return s + _line("M20 300h360", 4)


def watch():
    """Your Insurer Wants Your Step Count: a smartwatch with a heartbeat."""
    s = f'<rect x="120" y="20" width="80" height="60" rx="14" {B}/><rect x="120" y="220" width="80" height="70" rx="14" {B}/>'
    s += f'<rect x="90" y="70" width="140" height="160" rx="36" {E}/><rect x="104" y="84" width="112" height="132" rx="26" fill="#2A2140"/>'
    s += _line("M116 156h22l10-26 14 50 12-36 8 12h22", 4, "c") + f'<text x="160" y="200" text-anchor="middle" font-family="Inter, sans-serif" font-weight="700" font-size="18" fill="#fff">10,000</text>'
    s += f'<g transform="translate(320 170)"><path d="M0-70l56 20v40c0 40-28 64-56 78-28-14-56-38-56-78v-40z" fill="var(--sx-d)"/><path d="M-16 0l12 12 24-26" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>'
    return s + _line("M40 300h340", 4)

DRAW = {"house": house, "paper": paper, "esop": esop, "pie": pie, "village": village, "classroom": classroom, "deeptech": deeptech, "valley": valley, "clipboard": clipboard, "shield": shield, "clock": clock, "plate": plate, "watch": watch}


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

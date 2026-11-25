"""The drawn background of a company page, one scene per sector, all in ESV colours (tools/portfolio/render.py).

Colours: --sx-* on .co-page in css/styles.css. a sand, b pastel purple, c purple, d golden glow, e bronze, ink deep purple.
Each scene is drawn on a 1440 x 400 box, weighted to the right, standing on the bottom edge.
"""

SECTORS = {
    "Aerospace & Defence": "aerospace", "Climate & Mobility": "climate", "Commerce & Retail": "commerce", "Consumer Brands": "consumer", "Education": "education",
    "Food & Beverage": "food", "Healthcare": "health", "Software & Gaming": "software", "Supply Chain & Logistics": "supply", "Telecom & Infrastructure": "telecom",
}
A, B, C, D, E = (f'fill="var(--sx-{k})"' for k in "abcde")
W = 'fill="#fff"'


def _line(d, w=2, col="c", o=1, dash=""):
    dash = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="var(--sx-{col})" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{o}"{dash}/>'


def aerospace():
    s = f'<circle cx="1180" cy="640" r="360" {A}/><circle cx="1180" cy="660" r="330" {B} opacity=".45"/>'
    for k, r in enumerate((360, 450, 550, 660, 780)):
        s += f'<ellipse cx="1180" cy="560" rx="{r}" ry="{r * .82:.0f}" fill="none" stroke="var(--sx-b)" stroke-width="1.5" opacity="{.75 - k * .12:.2f}" stroke-dasharray="{"" if k % 2 else "2 10"}"/>'
    s += "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {W}/>' for x, y, r in ((640, 70, 3), (760, 150, 2), (860, 50, 2.5), (1010, 92, 3), (1330, 60, 3), (1400, 150, 2), (930, 210, 2), (560, 180, 2)))
    s += _line("M700 400C830 372 985 300 1072 160", 3, "c", .55, "1 12")
    s += f'<g transform="translate(1092 112) rotate(26)"><path d="M-9 24 0 62l9-38z" {D}/><path d="M-20 0-38 34l18-8zM20 0l18 34-18-8z" {C}/><path d="M0-58c18 18 24 44 20 78h-40c-4-34 2-60 20-78z" {W}/><path d="M0-58c9 9 15 20 18 34h-36c3-14 9-25 18-34z" {C}/><circle cy="-4" r="8" {D}/></g>'
    s += f'<g transform="translate(1300 190) rotate(-14) scale(1.05)"><path d="M82-10C60-18 30-18 6-16l-52-34h-16l26 36-28 2-16-14h-12l10 20-10 16h12l16-10 28 2-26 38h16l52-36c24 2 54 0 76-4z" {C} opacity=".9"/></g>'
    s += f'<g transform="translate(850 190)" fill="none" stroke="var(--sx-c)" stroke-linecap="round"><path d="M-46-18h92M-46-18v-8M46-18v-8" stroke-width="5"/><path d="M-72-28h52M20-28h52" stroke="var(--sx-b)" stroke-width="5"/><path d="M-16 6v12h-10M16 6v12h10" stroke-width="3"/></g><rect x="828" y="168" width="44" height="28" rx="11" {C}/><circle cx="850" cy="184" r="6" {W}/>'
    return s


def climate():
    s = f'<circle cx="1120" cy="170" r="104" {W} opacity=".7"/><circle cx="1120" cy="170" r="70" {E} opacity=".6"/>'
    s += f'<path d="M420 400C600 300 760 286 920 318s300 24 520-70v152z" {A}/>'

    def mill(x, y, h, r, rot):
        blades = "".join(f'<path d="M0 0C{r * .12:.1f} {-r * .25:.1f} {r * .08:.1f} {-r * .7:.1f} 0 {-r}C{-r * .07:.1f} {-r * .6:.1f} {-r * .06:.1f} {-r * .2:.1f} 0 0z" transform="rotate({rot + a})" {C}/>' for a in (0, 120, 240))
        return f'<g transform="translate({x} {y})"><path d="M-3 0h6l4 {h}h-14z" {W}/>{blades}<circle r="6" {W}/></g>'
    s += mill(820, 130, 190, 84, 12) + mill(960, 186, 140, 62, 48) + mill(1330, 96, 210, 92, 80)
    s += f'<path d="M560 400c150-70 330-84 480-46s270 10 400-44v90z" {B}/>'
    for k in range(4):
        s += f'<g transform="translate({1030 + k * 92} {330 - k * 9}) skewX(-18)"><rect width="78" height="38" rx="3" {C}/><path d="M26 0v38M52 0v38M0 19h78" stroke="var(--sx-a)" stroke-width="1.5"/></g>'
    s += f'<path d="M300 400c220-26 420-30 640-14s360 4 500-10v24z" {C}/>'
    # scooter on the road
    s += (f'<g transform="translate(700 298)" stroke-linecap="round" stroke-linejoin="round"><path d="M8 54C6 34 20 24 44 24h34l8 30z" {C}/>'
          f'<path d="M22 16h52q6 0 6 6v2H18q-2-8 4-8z" fill="var(--sx-ink)"/><path d="M80 58h26c10 0 14-6 18-16L112-18" fill="none" stroke="#fff" stroke-width="13"/>'
          f'<path d="M96-26h22l8 6" fill="none" stroke="var(--sx-ink)" stroke-width="5"/><path d="M114-14l14 4 8 46c-8-2-12 0-16 4z" {W}/><path d="M118 34c10-10 30-8 36 8" fill="none" stroke="#fff" stroke-width="6"/>'
          f'<circle cx="30" cy="66" r="18" fill="var(--sx-ink)"/><circle cx="30" cy="66" r="8" {W}/><circle cx="138" cy="66" r="18" fill="var(--sx-ink)"/><circle cx="138" cy="66" r="8" {W}/></g>')
    return s


def commerce():
    s = f'<circle cx="1190" cy="140" r="90" {E} opacity=".45"/><path d="M360 400C520 318 700 292 920 300s330-20 520-70v170z" {A}/>'
    for x, w, h, alt in ((660, 176, 132, 0), (850, 208, 168, 1), (1072, 188, 148, 0), (1274, 208, 176, 1)):
        y = 400 - h
        s += f'<rect x="{x}" y="{y}" width="{w - 14}" height="{h}" rx="6" {W}/>'
        step = (w + 2) / 6
        for i in range(6):
            s += f'<path d="M{x - 8 + i * step:.1f} {y + 14}h{step:.1f}v30a{step / 2:.1f} {step / 2:.1f} 0 0 1-{step:.1f} 0z" {C if (i + alt) % 2 else B}/>'
        s += f'<rect x="{x - 8}" y="{y}" width="{w + 2}" height="16" rx="5" {C}/>'
        ww, wh = w - 94, h - 98
        wx, dx = (x + 16, x + w - 62) if alt else (x + 64, x + 16)
        s += f'<rect x="{dx}" y="{y + 74}" width="32" height="{h - 74}" rx="4" {B}/><circle cx="{dx + 25}" cy="{y + 74 + (h - 74) * .55:.0f}" r="3" {W}/><rect x="{wx}" y="{y + 74}" width="{ww}" height="{wh}" rx="4" {A}/>'
        for k in range(int((ww - 4) / 24)):
            s += f'<circle cx="{wx + 16 + k * 24}" cy="{y + 74 + wh - 10}" r="9" {D if k % 2 else E}/>' if alt else f'<rect x="{wx + 7 + k * 24}" y="{y + 74 + wh - 24}" width="17" height="20" rx="3" {C if k % 2 else B}/>'
    return s + _line("M560 398h880", 4)


def consumer():
    s = f'<path d="M1010 400V190a130 130 0 0 1 260 0v210z" {A}/><path d="M1060 400V196a80 80 0 0 1 160 0v204z" {W} opacity=".75"/><circle cx="1140" cy="190" r="42" {D}/>'
    s += f'<path d="M762 400V270a84 84 0 0 1 168 0v130z" {A}/>'
    s += _line("M844 258c-6-60-34-90-58-104M844 258c0-70 4-104 14-140M846 258c10-54 34-82 62-92", 3)
    s += "".join(f'<ellipse cx="{x}" cy="{y}" rx="24" ry="11" transform="rotate({r} {x} {y})" {C if k % 2 else B}/>' for k, (x, y, r) in enumerate(((780, 148, 40), (812, 190, 20), (858, 112, -70), (846, 168, 60), (912, 160, -20), (884, 200, -50))))
    s += f'<path d="M832 400c-34-26-38-72-14-104 8-12 8-26 4-40h44c-4 14-4 28 4 40 24 32 20 78-14 104z" {C}/><path d="M806 338c24 8 52 8 76 0" fill="none" stroke="var(--sx-a)" stroke-width="3"/>'
    # lamp
    s += _line("M1354 400V210M1322 398h64", 6) + f'<path d="M1302 220l26-112h52l26 112z" {B}/><path d="M1302 220h104l-3-14h-98z" {C}/>'
    # blocks, cushion, books
    s += f'<rect x="1156" y="322" width="76" height="76" rx="8" {W} stroke="var(--sx-b)" stroke-width="2"/><circle cx="1194" cy="360" r="22" {B}/><path d="M1044 398a52 52 0 0 1 104 0z" {C}/><path d="M1240 398l36-72 36 72z" {E}/>'
    s += f'<circle cx="980" cy="374" r="24" {D}/><rect x="690" y="352" width="90" height="18" rx="5" {B}/><rect x="676" y="370" width="118" height="28" rx="6" {W}/>'
    return s + _line("M600 398h840", 4)


def education():
    s = "".join(_line(f"M520 {y}h920", 1.5, "a") for y in range(60, 400, 34))
    s += _line("M640 330c90-150 180-40 250-120s110-70 190-64", 2.5, "b", 1, "2 11")
    s += f'<g transform="translate(1090 90) rotate(-8)"><path d="M0 40 136-8 64 92 46 56z" {W}/><path d="M136-8 46 56l18 36z" {B}/><path d="M46 56l6 40 12-8z" {C}/></g>'
    for x, y, w, h, col in ((980, 356, 250, 44, "c"), (1000, 316, 210, 40, "d"), (974, 280, 236, 36, "w"), (1012, 246, 180, 34, "c")):
        f = W if col == "w" else f'fill="var(--sx-{col})"'
        s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" {f}/><rect x="{x + 18}" y="{y}" width="10" height="{h}" {A}/><rect x="{x + w - 46}" y="{y + h / 2 - 3}" width="28" height="6" rx="3" {A}/>'
    s += f'<path d="M1052 214v20c30 16 72 16 102 0v-20l-51 18z" {B}/><path d="M1103 172l94 34-94 34-94-34z" {C}/>' + _line("M1197 206v42", 4) + f'<circle cx="1197" cy="254" r="8" {C}/>'
    s += f'<rect x="1270" y="290" width="110" height="110" rx="10" {W}/><path d="M1300 345h50M1325 320v50" stroke="var(--sx-c)" stroke-width="8" stroke-linecap="round"/><rect x="1290" y="206" width="84" height="84" rx="10" {B}/><circle cx="1332" cy="248" r="22" {W}/><path d="M1332 130l42 76h-84z" {D}/>'
    s += f'<path d="M820 400 850 214l20-34 14 38-28 182z" {B}/><path d="M850 214l20-34 14 38z" {W}/><path d="M863 192l7-12 5 14z" {C}/><path d="M884 400h74l-74-120z" {C} opacity=".55"/>'
    return s + _line("M640 398h800", 4)


def food():
    s = f'<circle cx="1120" cy="250" r="220" {A} opacity=".8"/>'
    for k, (x, y, r) in enumerate(((700, 120, 12), (760, 250, 22), (650, 300, 9), (830, 80, 16), (900, 160, 10), (1010, 70, 26), (1380, 110, 18), (1330, 60, 10), (1410, 220, 12), (1030, 330, 14), (1260, 80, 12), (560, 200, 8))):
        s += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#fff" if k % 2 else "none"}" stroke="var(--sx-b)" stroke-width="2" opacity=".85"/>'
    s += _line("M1146 150 1176 40l40-14", 8) + f'<path d="M1056 140h150l-18 258h-114z" {W} opacity=".92"/><path d="M1063 206h136l-13 188h-110z" {E}/>'
    s += "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {W} opacity=".8"/>' for x, y, r in ((1096, 350, 8), (1130, 300, 6), (1160, 360, 10), (1120, 250, 7), (1166, 270, 5)))
    s += f'<g transform="translate(1060 152)"><circle r="44" {D}/><circle r="36" {W}/>' + "".join(f'<path d="M0-5-11-29a31 31 0 0 1 22 0z" {B} transform="rotate({a})"/>' for a in range(0, 360, 60)) + "</g>"
    s += f'<path d="M830 270h150l-20 128H850z" {C}/><path d="M820 256h170v18H820z" {W}/><path d="M842 318h126l-6 40H848z" {A}/>'
    s += _line("M872 232c-14-22 14-34 0-60M906 232c-14-26 14-40 0-70M940 232c-14-22 14-34 0-60", 4, "b")
    s += f'<path d="M1270 250l10-18h80l10 18v132l-10 16h-80l-10-16z" {C}/><path d="M1270 284h100v70h-100z" {W}/><circle cx="1320" cy="319" r="22" {D}/><rect x="1288" y="224" width="64" height="10" rx="4" {B}/>'
    return s + _line("M700 398h740", 4)


def health():
    s = f'<rect x="1060" y="50" width="120" height="340" rx="28" {A}/><rect x="950" y="160" width="340" height="120" rx="28" {A}/>'
    s += _line("M420 222h270l22-54 34 120 34-196 36 162 20-32h130l24-46 30 92 28-46h420", 3.5, "c", .8)

    def pill(x, y, r, l=120, h=48):
        return f'<g transform="translate({x} {y}) rotate({r})"><rect x="{-l / 2}" y="{-h / 2}" width="{l}" height="{h}" rx="{h / 2}" {W}/><path d="M0 {-h / 2}h{l / 2 - h / 2}a{h / 2} {h / 2} 0 0 1 0 {h}H0z" {C}/><path d="M{-l / 2 + 22} {-h / 2 + 11}h{l / 2 - 30}" stroke="var(--sx-a)" stroke-width="6" stroke-linecap="round"/></g>'

    def tab(x, y, r):
        return f'<circle cx="{x}" cy="{y}" r="{r}" {W}/><path d="M{x - r * .55:.0f} {y}h{r * 1.1:.0f}" stroke="var(--sx-b)" stroke-width="3" stroke-linecap="round"/>'
    s += f'<g transform="translate(1180 318) rotate(-12)"><rect x="-150" y="-62" width="300" height="130" rx="16" {B}/>' + "".join(f'<ellipse cx="{-105 + i * 70}" cy="{-28 + j * 60}" rx="26" ry="20" {W}/>' for i in range(4) for j in range(2)) + "</g>"
    s += pill(900, 330, -24) + pill(1370, 150, 32, 110, 44) + pill(830, 100, 18, 92, 36) + tab(1000, 352, 26) + tab(760, 340, 18) + tab(1390, 320, 24) + tab(1270, 84, 18)
    return s


def software():
    s = "".join(f'<circle cx="{x}" cy="{y}" r="1.6" {B}/>' for x in range(560, 1440, 32) for y in range(24, 400, 32))
    s += f'<rect x="900" y="60" width="430" height="290" rx="16" {W}/><path d="M916 60h398a16 16 0 0 1 16 16v22H900V76a16 16 0 0 1 16-16z" {A}/>' + "".join(f'<circle cx="{926 + k * 22}" cy="79" r="6" {C if k == 0 else B}/>' for k in range(3))
    for k, (ind, w, col) in enumerate(((0, 90, "c"), (1, 150, "b"), (2, 120, "a"), (2, 170, "b"), (1, 70, "c"), (0, 120, "b"), (1, 150, "a"))):
        s += f'<rect x="{930 + ind * 28}" y="{124 + k * 28}" width="{w}" height="10" rx="5" fill="var(--sx-{col})"/><rect x="{940 + ind * 28 + w}" y="{124 + k * 28}" width="{40 + (k * 37) % 50}" height="10" rx="5" {A}/>'
    pts = [(700, 110), (780, 210), (690, 300), (840, 120), (830, 320)]
    s += "".join(_line(f"M{pts[i][0]} {pts[i][1]}L{pts[j][0]} {pts[j][1]}", 2, "b") for i, j in ((0, 1), (1, 2), (1, 3), (1, 4), (0, 3), (2, 4))) + _line("M840 120l60 30M830 320l70-30", 2, "b")
    s += "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {f}/>' for (x, y), r, f in zip(pts, (14, 22, 12, 12, 16), (W, C, D, E, W)))
    s += f'<g transform="translate(1286 322)"><path d="M-110-34c10-26 40-30 62-20h96c22-10 52-6 62 20 14 36 22 84-2 96-26 12-46-34-64-40h-88c-18 6-38 52-64 40-24-12-16-60-2-96z" {C}/><path d="M-66-26v36M-84-8h36" stroke="#fff" stroke-width="10" stroke-linecap="round"/><circle cx="52" cy="4" r="8" {W}/><circle cx="76" cy="-18" r="8" {D}/></g>'
    for x, y, f in ((1364, 60, C), (1388, 60, B), (1388, 36, A), (1412, 84, B), (1412, 36, C), (600, 360, B), (624, 360, A), (624, 336, C), (648, 360, A)):
        s += f'<rect x="{x}" y="{y}" width="20" height="20" rx="3" {f}/>'
    return s


def supply():
    s = _line("M480 330c140 0 150-150 300-150s140 120 290 120 160-190 370-190", 3, "b", 1, "2 12")

    def box(x, y, n, light=False):   # isometric carton, (x, y) = left corner of the lid
        h = n / 2
        return (f'<g transform="translate({x} {y})"><path d="M0 0 {n}-{h}l{n} {h}L{n} {h}z" {W if light else A}/><path d="M0 0 {n} {h}v{n}L0 {n - 0:.0f}z" {E}/>'
                f'<path d="M{2 * n} 0 {n} {h}v{n}l{n}-{h}z" {C}/><path d="M{n * .4:.0f} {-h * .4:.1f}l{n} {h}h{n * .2:.0f}l-{n}-{h}z" {W} opacity=".0"/><path d="M{n * .42:.1f}-{h * .42:.1f}L{n * 1.42:.1f} {h * .58:.1f}l{n * .16:.1f}-{h * .16:.1f}L{n * .58:.1f}-{h * .58:.1f}z" {W} opacity=".75"/></g>')
    n = 70
    # back to front, bottom to top, all on a floor at y = 400
    for x, y, light in ((1000, 293, 0), (1150, 293, 0), (1300, 293, 1), (1075, 220, 1), (1225, 220, 0), (1150, 147, 0)):
        s += box(x, y, n, light)

    def pin(x, y):
        return f'<g transform="translate({x} {y})"><path d="M0 0c-16-22-24-32-24-46a24 24 0 0 1 48 0c0 14-8 24-24 46z" {C}/><circle cy="-46" r="9" {W}/></g>'
    s += pin(780, 178) + pin(580, 296)
    s += f'<g transform="translate(730 300)"><rect width="150" height="78" rx="6" {W}/><path d="M154 22h44l26 30v26h-70z" {C}/><path d="M166 32h26l14 18h-40z" {A}/><path d="M16 22h70M16 42h44" stroke="var(--sx-b)" stroke-width="8" stroke-linecap="round"/><circle cx="38" cy="82" r="17" {C}/><circle cx="38" cy="82" r="7" {W}/><circle cx="184" cy="82" r="17" {C}/><circle cx="184" cy="82" r="7" {W}/></g>'
    return s + _line("M560 399h880", 4)


def telecom():
    s = "".join(f'<path d="M{1180 - r} 120a{r} {r} 0 0 1 {2 * r} 0" fill="none" stroke="var(--sx-b)" stroke-width="{3 if k < 3 else 2}" opacity="{.95 - k * .13:.2f}"/>' for k, r in enumerate((50, 90, 135, 190, 255, 330)))
    s += _line("M1180 134 1120 400M1180 134l60 266M1168 190h24M1156 240h48M1144 292h72M1132 344h96M1168 190l36 50M1192 190l-36 50M1156 240l60 52M1204 240l-60 52M1144 292l84 52M1216 292l-84 52", 4) + f'<circle cx="1180" cy="120" r="14" {C}/>'
    s += _line("M930 400V262M902 252a40 40 0 0 1 56 0M882 230a68 68 0 0 1 96 0M1370 400V242M1344 232a36 36 0 0 1 52 0M1326 212a62 62 0 0 1 88 0", 3.5, "c", .8) + f'<circle cx="930" cy="266" r="7" {C}/><circle cx="1370" cy="246" r="7" {C}/>'
    for k in range(9):
        y = 404 - k * 9
        stroke = ("#fff", "var(--sx-b)", "var(--sx-c)")[k % 3]
        s += f'<path d="M-20 {y + 10}C440 {y + 6} 640 {y - 80 + k * 10} 900 {y - 50 + k * 7}S1240 {y + 18} 1440 {y - 26 + k * 3}" fill="none" stroke="{stroke}" stroke-width="{2.5 if k % 3 else 4}" opacity=".75"/>'
    return s


DRAW = {"aerospace": aerospace, "climate": climate, "commerce": commerce, "consumer": consumer, "education": education, "food": food, "health": health, "software": software, "supply": supply, "telecom": telecom}


def scene(sector):
    return f'<svg class="co-scene" viewBox="0 0 1440 400" preserveAspectRatio="xMaxYMax slice" aria-hidden="true" focusable="false">{DRAW[SECTORS[sector]]()}</svg>'

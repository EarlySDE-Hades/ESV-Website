"""Build the inner pages from index.html's head, header and footer plus each page's own <main>.

    about.html   <- tools/about/main.html
    team.html    <- tools/team/main.html
    press.html   <- tools/press/main.html (+ tools/press/press.json)
    events.html  <- tools/events/main.html
    event-seed-to-success.html  <- tools/events/seed-to-success.html

Run after changing the shared header/footer in index.html, or either main.html:

    python tools/team/build.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / "index.html").read_text(encoding="utf-8")

head, rest = src.split("<body>", 1)
header = rest[rest.index("  <a class=\"skip-link\""):rest.index("  <main id=\"main\">")]
footer = rest[rest.index("  <!-- ============================== Footer"):]
head = re.sub(r"<title>.*?</title>", "<title>Earlyseed Ventures</title>", head)

# output file, source of <main>, meta description, nav link text to mark as the current page
PAGES = [
    ("prologue.html", "tools/prologue/main.html", "Prologue by Earlyseed Ventures prepares early-stage founders for fundraising: the deck, the numbers and the understanding to defend both.", "Prologue"),
    ("about.html", "tools/about/main.html", "Earlyseed Ventures is a boutique investment banking firm in Mumbai, helping tech start-ups raise seed to Series A rounds.", "About"),
    ("team.html", "tools/team/main.html", "The leadership team, strategic growth partners and team behind Earlyseed Ventures.", "Team"),
    ("press.html", "tools/press/main.html", "Us in the News: media coverage, funding announcements and industry conversations featuring Earlyseed Ventures and its co-founders.", "Our Press"),
    ("events.html", "tools/events/main.html", "Founder meet-ups, investor sessions and campus programmes from Earlyseed Ventures.", "Events"),
    ("event-seed-to-success.html", "tools/events/seed-to-success.html", "From seed to success: a recap of the Earlyseed Ventures evening for founders, investors and ecosystem leaders.", "-"),
]


# Extra <head> tags for a single page: the Prologue page uses IBM Plex Sans, per the Prologue brand guide
EXTRA_HEAD = {
    "prologue.html": '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&display=swap" />\n',
}


def relink(html, out, label):
    # Section anchors live on the homepage
    html = re.sub(r'href="#(?!main\b)([\w-]+)"', r'href="index.html#\1"', html)
    html = html.replace('href="/"', 'href="index.html"')
    for text in (label, label + " Us"):
        html = html.replace(f'<a href="{out}">{text}</a>', f'<a href="{out}" aria-current="page">{text}</a>')
    return html


# Pages whose <main> has {{…}} placeholders filled from data
import sys
sys.path.insert(0, str(ROOT / "tools" / "press"))
from render import render as render_press   # noqa: E402
FILLERS = {"press.html": render_press}


for out, main_src, description, label in PAGES:
    main = (ROOT / main_src).read_text(encoding="utf-8")
    if out in FILLERS:
        for key, value in FILLERS[out]().items():
            main = main.replace(key, value)
        assert "{{" not in main, f"unfilled placeholder in {out}"
    page_head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + description, head)
    if out in EXTRA_HEAD:
        page_head = page_head.replace("</head>", EXTRA_HEAD[out] + "</head>")
    page = page_head + "<body>\n" + relink(header, out, label) + main + "\n" + relink(footer, out, label)
    (ROOT / out).write_text(page, encoding="utf-8", newline="\n")
    print("wrote", out)

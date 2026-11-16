"""Build the inner pages from index.html's head, header and footer plus each page's own <main>.

    team.html    <- tools/team/main.html
    events.html  <- tools/events/main.html

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
    ("team.html", "tools/team/main.html", "The leadership team, strategic growth partners and team behind Earlyseed Ventures.", "Team"),
    ("events.html", "tools/events/main.html", "Founder meet-ups, investor sessions and campus programmes from Earlyseed Ventures.", "Events"),
]


def relink(html, out, label):
    # Section anchors live on the homepage
    html = re.sub(r'href="#(?!main\b)([\w-]+)"', r'href="index.html#\1"', html)
    html = html.replace('href="/"', 'href="index.html"')
    return html.replace(f'<a href="{out}">{label}</a>', f'<a href="{out}" aria-current="page">{label}</a>')


for out, main_src, description, label in PAGES:
    main = (ROOT / main_src).read_text(encoding="utf-8")
    page_head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + description, head)
    page = page_head + "<body>\n" + relink(header, out, label) + main + "\n" + relink(footer, out, label)
    (ROOT / out).write_text(page, encoding="utf-8", newline="\n")
    print("wrote", out)

"""Build team.html from index.html's head, header and footer plus tools/team/main.html.

Run after changing the shared header/footer in index.html:  python tools/team/build.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / "index.html").read_text(encoding="utf-8")
main = (Path(__file__).parent / "main.html").read_text(encoding="utf-8")

head, rest = src.split("<body>", 1)
header = rest[rest.index("  <a class=\"skip-link\""):rest.index("  <main id=\"main\">")]
footer = rest[rest.index("  <!-- ============================== Footer"):]

head = re.sub(r"<title>.*?</title>", "<title>Team — Earlyseed Ventures</title>", head)
head = re.sub(r'(<meta name="description" content=")[^"]*', r"\1The leadership team behind Earlyseed Ventures.", head)

def relink(html):
    # Section anchors live on the homepage
    html = re.sub(r'href="#(?!main\b)([\w-]+)"', r'href="index.html#\1"', html)
    html = html.replace('href="/"', 'href="index.html"')
    html = html.replace('<a href="team.html">Team</a>', '<a href="team.html" aria-current="page">Team</a>')
    return html

page = head + "<body>\n" + relink(header) + main + "\n" + relink(footer)
(ROOT / "team.html").write_text(page, encoding="utf-8", newline="\n")
print("wrote team.html")

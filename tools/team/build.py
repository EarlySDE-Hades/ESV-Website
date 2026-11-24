"""Build the inner pages from index.html's head, header and footer plus each page's own <main>.

    about.html   <- tools/about/main.html
    team.html    <- tools/team/main.html
    team-<slug>.html  <- tools/team/profiles.py (the profile templates in main.html + profiles.json)
    press.html   <- tools/press/main.html (+ tools/press/press.json)
    perspectives.html, perspective-<slug>.html  <- tools/perspectives/ (+ posts.json)
    portfolio.html, portfolio-<slug>.html  <- tools/portfolio/ (+ companies.json)
    events.html  <- tools/events/main.html
    event-seed-to-success.html  <- tools/events/seed-to-success.html
    titles, descriptions, canonical links, structured data, sitemap.xml and robots.txt  <- tools/seo/seo.py

Run after changing the shared header/footer in index.html, or either main.html:

    python tools/team/build.py
"""
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / "index.html").read_text(encoding="utf-8")

head, rest = src.split("<body>", 1)
header = rest[rest.index("  <a class=\"skip-link\""):rest.index("  <main id=\"main\">")]
footer = rest[rest.index("  <!-- ============================== Footer"):]

# output file, source of <main>, meta description, nav link text to mark as the current page
PAGES = [
    ("prologue.html", "tools/prologue/main.html", "Prologue by Earlyseed Ventures prepares early-stage founders for fundraising: the deck, the numbers and the understanding to defend both.", "Prologue"),
    ("about.html", "tools/about/main.html", "Earlyseed Ventures is a boutique investment banking firm in Mumbai, helping tech start-ups raise seed to Series A rounds.", "About"),
    ("team.html", "tools/team/main.html", "The leadership team, strategic growth partners and team behind Earlyseed Ventures.", "Team"),
    ("portfolio.html", "tools/portfolio/main.html", "The companies Earlyseed Ventures has raised for and invested in, from rural commerce and space-tech to AI and consumer brands.", "Our Portfolio"),
    ("perspectives.html", "tools/perspectives/main.html", "Our Perspectives: fundraising playbooks and founder stories from Earlyseed Ventures.", "Our Perspectives"),
    ("press.html", "tools/press/main.html", "Us in the News: media coverage, funding announcements and industry conversations featuring Earlyseed Ventures and its co-founders.", "Our Press"),
    ("bootcamps.html", "tools/bootcamps/main.html", "Founder bootcamps on campus: Earlyseed Ventures works with universities and incubators on business planning, pitch decks, financial projections and access to investors.", "Bootcamps"),
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
import importlib.util


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


seo = _load("seo", "tools/seo/seo.py")
press_render = _load("press_render", "tools/press/render.py")
portfolio_render = _load("portfolio_render", "tools/portfolio/render.py")
perspectives_render = _load("perspectives_render", "tools/perspectives/render.py")
profiles = _load("profiles", "tools/team/profiles.py")
bootcamps_render = _load("bootcamps_render", "tools/bootcamps/render.py")
FILLERS = {"press.html": press_render.render, "perspectives.html": perspectives_render.render, "portfolio.html": portfolio_render.render_portfolio, "bootcamps.html": bootcamps_render.render}


written = []


def write(out, main, description, label, title=None):
    assert "{{" not in main, f"unfilled placeholder in {out}"
    page_head = seo.apply(head, out, description, title)
    written.append(out)
    if out in EXTRA_HEAD:
        page_head = page_head.replace("</head>", EXTRA_HEAD[out] + "</head>")
    page = page_head + "<body>\n" + relink(header, out, label) + main + "\n" + relink(footer, out, label)
    (ROOT / out).write_text(page, encoding="utf-8", newline="\n")
    print("wrote", out)


for out, main_src, description, label in PAGES:
    main = (ROOT / main_src).read_text(encoding="utf-8")
    if out in FILLERS:
        for key, value in FILLERS[out]().items():
            main = main.replace(key, value)
    write(out, main, description, label)

# One page per portfolio company (portfolio-<slug>.html)
for out, main, description in portfolio_render.company_pages():
    write(out, main, description, "Our Portfolio")

# One page per leader and growth partner (team-<slug>.html)
for out, main, description in profiles.pages():
    write(out, main, description, "Team")

# One page per article hosted on this site (perspective-<slug>.html)
for out, main, description in perspectives_render.article_pages():
    heading = re.search(r'id="post-title"[^>]*>([^<]+)', main).group(1)
    write(out, main, description, "Our Perspectives", f"{unescape(heading)} | Earlyseed Ventures")

# index.html is edited by hand; only its search tags are written here
(ROOT / "index.html").write_text(seo.apply(src, "index.html", ""), encoding="utf-8", newline="\n")
seo.write_sitemap(["index.html"] + written)
print("wrote index.html search tags, sitemap.xml, robots.txt")

"""Render the Portfolio page and one page per company from tools/portfolio/companies.json.

Called by tools/team/build.py:
  render_portfolio()  -> placeholder values for tools/portfolio/main.html
  company_pages()     -> [(output file, <main> html, meta description)] from tools/portfolio/company.html
"""
import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXT = '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M6 3.5h6.5V10M12.5 3.5 4 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M3 8h9.5M8.5 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def _companies():
    return json.loads((HERE / "companies.json").read_text(encoding="utf-8"))["companies"]


def page_of(c):
    return f"portfolio-{c['slug']}.html" if c.get("description") else None


def _logo(c, cls):
    f = next(iter(sorted((ROOT / "assets/logos/portfolio").glob(f"{c['slug']}.*"))), None)
    return f'<img class="{cls}" src="assets/logos/portfolio/{f.name}" alt="" />' if f else ""


def render_portfolio():
    cs = _companies()
    sectors = sorted({c["sector"] for c in cs})
    cities = {c["location"] for c in cs if c.get("location")}
    cards = []
    for i, c in enumerate(cs):
        lazy = "" if i < 6 else 'loading="lazy" '
        search = " ".join(filter(None, [c["name"], c["sector"], c.get("tag"), c.get("location"), c.get("short")])).lower()
        meta = " · ".join(filter(None, [c.get("tag"), c.get("location")]))
        cards.append(f'''          <li class="pf-card" data-sector="{escape(c["sector"])}" data-search="{escape(search)}">
            <a class="pf-card__link" href="{page_of(c)}">
              <span class="pf-card__media"><img src="assets/portfolio/{c["slug"]}.webp" alt="" width="450" height="450" {lazy}decoding="async" /><span class="pf-card__go" aria-hidden="true">{ARROW}</span></span>
              <span class="visually-hidden">{escape(c["name"])}{", " + escape(meta) if meta else ""}</span>
            </a>
          </li>''')
    options = "\n".join(f'              <option value="{escape(s)}">{escape(s)}</option>' for s in sectors)
    return {
        "{{GRID}}": "\n".join(cards),
        "{{COUNT}}": str(len(cs)),
        "{{SECTOR_COUNT}}": str(len(sectors)),
        "{{CITY_COUNT}}": str(len(cities)),
        "{{SECTOR_OPTIONS}}": options,
    }


def _press_tiles(topic):
    if not topic:
        return ""
    press = json.loads((ROOT / "tools/press/press.json").read_text(encoding="utf-8"))
    items = [i for i in press["items"] if i["topic"] == topic and i["verificationStatus"] == "verified"]
    rank = {"editorial": 0, "roundup": 1, "press-release": 2, "sponsored": 3, "aggregator": 4}
    items.sort(key=lambda i: (not i["featured"], rank[i["coverageType"]], i["date"] or ""))
    if not items:
        return ""
    tiles = []
    for n, i in enumerate(items[:3]):
        cls = "co-media__tile co-media__tile--lead" if n == 0 else "co-media__tile"
        when = f'<time datetime="{i["date"]}">{escape(i["dateLabel"])}</time>' if i.get("date") else escape(i["dateLabel"])
        tiles.append(f'''          <a class="{cls}" href="{escape(i["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{escape(i["title"])}, {escape(i["publication"])} (opens in a new tab)">
            <span class="co-media__pub">{escape(i["publication"])}</span>
            <span class="co-media__title">{escape(i["title"])}</span>
            <span class="co-media__meta">{when} · {escape(i["typeLabel"])} {EXT}</span>
          </a>''')
    return f'''      <section class="co-media" aria-labelledby="co-media-title">
        <h2 class="co-label" id="co-media-title">Blogs &amp; Media</h2>
        <div class="co-media__grid co-media__grid--{len(tiles)}">
{chr(10).join(tiles)}
        </div>
        <a class="btn co-media__more" href="press.html#coverage">View more</a>
      </section>'''


def _group(title, items):
    return (f'<div class="co-facts__group"><h2 class="co-label">{title}</h2><ul role="list">'
            + "".join(f"<li>{escape(t)}</li>" for t in items) + "</ul></div>")


def company_pages():
    template = (HERE / "company.html").read_text(encoding="utf-8")
    cs = _companies()
    pages = []
    for n, c in enumerate(cs):
        logo = _logo(c, "co-hero__logo") or f'<span class="co-hero__wordmark" aria-hidden="true">{escape(c["name"])}</span>'
        side = []
        if c.get("team"):
            side.append(_group("Team", c["team"]))
        if c.get("milestones"):
            side.append(_group("Milestones", c["milestones"]))
        if c.get("location"):
            side.append(_group("Based in", [c["location"]]))
        tags = f'<li class="co-tag">{escape(c["sector"])}</li>'
        if c.get("tag"):
            tags += f'<li class="co-tag co-tag--soft">{escape(c["tag"])}</li>'
        site = ""
        if c.get("website"):
            host = c["website"].split("//", 1)[-1].split("/", 1)[0].removeprefix("www.")
            site = (f'<a class="co-site" href="{escape(c["website"])}" target="_blank" rel="noopener noreferrer" '
                    f'aria-label="{escape(c["name"])} website (opens in a new tab)">{escape(host)} {EXT}</a>')
        nxt = cs[(n + 1) % len(cs)]
        fill = {
            "{{LOGO}}": logo,
            "{{NAME}}": escape(c["name"]),
            "{{DESCRIPTION}}": escape(c["description"]),
            "{{FACTS}}": "\n            ".join(side),
            "{{TAGS}}": tags,
            "{{SITE}}": site,
            "{{MEDIA}}": _press_tiles(c.get("pressTopic")),
            "{{NEXT_HREF}}": page_of(nxt),
            "{{NEXT_NAME}}": escape(nxt["name"]),
        }
        main = template
        for k, v in fill.items():
            main = main.replace(k, v)
        pages.append((page_of(c), main, c["short"]))
    return pages

"""Render the Us in the News page from tools/press/press.json.

Called by tools/team/build.py, which fills the {{…}} placeholders in tools/press/main.html.
Only entries with verificationStatus "verified" are published.
"""
import json
from datetime import date
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M6 3.5h6.5V10M12.5 3.5 4 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
# Story order on the page: newest first
STORY_ORDER = ["startup-mixer", "electriq", "alchemyst", "skill-titans"]
# Featured order: the established publications first, as listed in the brief
FEATURED_ORDER = ["Forbes India", "Moneycontrol", "Financial Express", "Entrepreneur India", "The Tribune", "YourStory", "Inc42"]
# Within a story: news first, aggregators last
TYPE_RANK = {"editorial": 0, "roundup": 1, "press-release": 2, "sponsored": 3, "aggregator": 4}
# Decorative "body copy" lines for the front-page columns (widths in %)
LINES = [100, 96, 100, 88, 100, 92, 64]


def _date_label(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def _link(item, cls, text):
    a = escape(item["publication"])
    t = escape(item["title"])
    return (f'<a class="{cls}" href="{escape(item["url"])}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="Read article: {t}, {a} (opens in a new tab)">{text}</a>')


def _also(item):
    syn = item.get("syndicated") or []
    if not syn:
        return ""
    links = ", ".join(
        f'<a href="{escape(s["url"])}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{escape(s["publication"])} copy of this story (opens in a new tab)">{escape(s["publication"])}</a>'
        for s in syn)
    return f'<p class="press-card__also">Also carried by {links}</p>'


def _time(item):
    if item.get("date"):
        return f'<time datetime="{item["date"]}">{escape(item["dateLabel"])}</time>'
    return f'<span>{escape(item["dateLabel"])}</span>'


def render():
    data = json.loads((HERE / "press.json").read_text(encoding="utf-8"))
    stories = data["stories"]
    items = [i for i in data["items"] if i["verificationStatus"] == "verified"]
    by_story = {s: sorted([i for i in items if i["topic"] == s], key=lambda i: (not i["featured"], i["date"] or "")) for s in STORY_ORDER}

    # Featured carousel cards
    featured = sorted([i for i in items if i["featured"]],
                      key=lambda i: FEATURED_ORDER.index(i["publication"]) if i["publication"] in FEATURED_ORDER else 99)
    cards = []
    for i in featured:
        cards.append(f'''            <li class="press-card" data-type="{i["coverageType"]}">
              <article class="press-card__inner">
                <p class="press-card__pub">{escape(i["publication"])}</p>
                <p class="press-card__meta">{_time(i)}<span class="press-card__type">{escape(i["typeLabel"])}</span></p>
                <h3 class="press-card__title">{escape(i["title"])}</h3>
                <p class="press-card__topic">{escape(stories[i["topic"]])}</p>
                <p class="press-card__mention">{escape(i["mentions"])}</p>
                {_also(i)}
                {_link(i, "press-card__link", "Read article " + EXT)}
              </article>
            </li>''')

    # Front page: one column per story, led by its best-known piece
    cols = []
    for s in STORY_ORDER:
        lead = by_story[s][0]
        photo = ('\n              <img class="paper__photo" src="assets/perspectives/skill-titans.webp" alt="" loading="lazy" decoding="async" />'
                 if s == "skill-titans" else "")
        lines = "".join(f'<span style="--w:{w}%"></span>' for w in LINES[: 5 if photo else 7])
        cols.append(f'''            <section class="paper__col" aria-label="{escape(stories[s])}">
              <p class="paper__kicker">{escape(stories[s])}</p>
              <h2 class="paper__story">{_link(lead, "paper__story-link", escape(lead["title"]))}</h2>
              <p class="paper__by">{escape(lead["publication"])} · {escape(lead["dateLabel"])}</p>{photo}
              <div class="paper__lines" aria-hidden="true">{lines}</div>
            </section>''')

    # Full list grouped by story
    groups = []
    for s in STORY_ORDER:
        rows = []
        for i in sorted(by_story[s], key=lambda i: (FEATURED_ORDER.index(i["publication"]) if i["publication"] in FEATURED_ORDER else 99, TYPE_RANK[i["coverageType"]], i["date"] or "")):
            rows.append(f'''              <li class="press-row" data-type="{i["coverageType"]}">
                <span class="press-row__pub">{escape(i["publication"])}</span>
                {_link(i, "press-row__title", escape(i["title"]) + " " + EXT)}
                <span class="press-row__meta">{_time(i)} · {escape(i["typeLabel"])}</span>
                {_also(i).replace("press-card__also", "press-row__also")}
              </li>''')
        groups.append(f'''          <section class="press-group" aria-label="{escape(stories[s])}">
            <h3 class="press-group__title">{escape(stories[s])}</h3>
            <ul class="press-group__list" role="list">
{chr(10).join(rows)}
            </ul>
          </section>''')

    years = sorted(i["date"][:4] for i in items if i.get("date"))
    return {
        "{{FEATURED}}": "\n".join(cards),
        "{{FRONT_PAGE}}": "\n".join(cols),
        "{{ALL}}": "\n".join(groups),
        "{{ARTICLE_COUNT}}": str(len(items)),
        "{{STORY_COUNT}}": str(len(STORY_ORDER)),
        "{{COVERAGE_SPAN}}": f"Coverage {years[0]} to {years[-1]}",
    }

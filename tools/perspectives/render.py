"""Render the Our Perspectives page (and any articles hosted here) from tools/perspectives/posts.json.

Called by tools/team/build.py:
  render()        -> placeholder values for tools/perspectives/main.html
  article_pages() -> [(output file, <main> html, meta description)] for posts without a "url"
"""
import json
from datetime import date
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M6 3.5h6.5V10M12.5 3.5 4 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M3 8h9.5M8.5 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
BACK = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M10 3.5 5.5 8l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
COVERS = ["lilac", "sand", "violet", "rose", "crema", "bronze", "ink"]   # cover colours, in turn


def _data():
    d = json.loads((HERE / "posts.json").read_text(encoding="utf-8"))
    d["posts"].sort(key=lambda p: p["date"], reverse=True)
    return d


def _date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b')} {d.year}"


def _href(p):
    return p.get("url") or f"perspective-{p['slug']}.html"


def _attrs(p):
    return ' target="_blank" rel="noopener noreferrer"' if _href(p).startswith("http") else ""


def _mins(p):
    return f" · {max(1, round(p['words'] / 220))} min read" if p.get("words") else ""


def _new_tab(p):
    return '<span class="visually-hidden"> (opens in a new tab)</span>' if _attrs(p) else ""


def render():
    d = _data()
    posts, series = d["posts"], d["series"]
    names = {s["id"]: s["name"] for s in series}

    contents = []
    for s in series:
        n = sum(p["series"] == s["id"] for p in posts)
        contents.append(f'                <li><a href="perspectives.html#{s["id"]}" data-series-link><span class="book__entry">{escape(s["name"])}</span>'
                        f'<span class="book__dots" aria-hidden="true"></span><span class="book__num{"" if n else " book__num--soon"}">{n or "Soon"}{"<span class=visually-hidden> articles</span>" if n else ""}</span></a></li>')

    covers, k = [], 0
    for p in posts:
        if p.get("photo"):
            face = f'<img class="cover__photo" src="{p["photo"]}" alt="" loading="lazy" decoding="async" draggable="false" />'
            tone = "photo"
        else:
            face = f'<span class="cover__mark" aria-hidden="true">{escape(p.get("mark", ""))}</span>'
            tone = COVERS[k % len(COVERS)]
            k += 1
        covers.append(f'''            <li class="cover">
              <a class="cover__link" href="{_href(p)}"{_attrs(p)} draggable="false">
                <span class="cover__face cover__face--{tone}">
                  <span class="cover__top"><span>{escape(names[p["series"]])}</span><span>{escape(p["label"])}</span></span>
                  {face}
                  <span class="cover__title">{escape(p.get("short", p["title"]))}</span>
                </span>
                <span class="cover__meta"><span><time datetime="{p["date"]}">{_date(p["date"])}</time>{_mins(p)}</span><span class="cover__go" aria-hidden="true">{EXT if _attrs(p) else ARROW}</span></span>{_new_tab(p)}
              </a>
            </li>''')

    groups = []
    for n, s in enumerate(series):
        mine = [p for p in posts if p["series"] == s["id"]]
        if mine:
            rows = "\n".join(f'''                <li><a class="pv-row" href="{_href(p)}"{_attrs(p)}>
                  <span class="pv-row__label">{escape(p["label"])}</span>
                  <span class="pv-row__text"><span class="pv-row__title">{escape(p["title"])}</span><span class="pv-row__sum">{escape(p["summary"])}</span></span>
                  <span class="pv-row__meta"><time datetime="{p["date"]}">{_date(p["date"])}</time> {EXT if _attrs(p) else ARROW}</span>{_new_tab(p)}
                </a></li>''' for p in mine)
            body = f'<ul class="pv-rows" role="list">\n{rows}\n              </ul>'
            count = f'{len(mine)} article{"s" if len(mine) != 1 else ""}'
        else:
            count = escape(s.get("soon", "First article coming soon"))
            body = f'<p class="pv-soon">{count}.</p>'
        art = (f'<img class="pv-series__art" src="assets/perspectives/{s["photo"]}" alt="" style="object-position:{s["focus"]}" loading="lazy" decoding="async" />'
               if s.get("photo") else
               f'<img class="pv-series__icon" src="assets/icons/sectors/{s["icon"]}.webp" alt="" width="112" height="112" loading="lazy" decoding="async" />' if s.get("icon") else "")
        groups.append(f'''          <details class="pv-series" id="{s["id"]}"{" open" if n == 0 else ""}>
            <summary><span class="pv-series__n" aria-hidden="true">{n + 1}</span><h3 class="pv-series__name">{escape(s["name"])}</h3><span class="pv-series__count">{count}</span><span class="pv-series__plus" aria-hidden="true"></span></summary>
            <div class="pv-series__body">
              <div class="pv-series__side">{art}<p>{escape(s["about"])}</p></div>
              <div class="pv-series__main">{body}</div>
            </div>
          </details>''')
    return {
        "{{CONTENTS}}": "\n".join(contents).replace("class=visually-hidden", 'class="visually-hidden"'),
        "{{COVERS}}": "\n".join(covers),
        "{{SERIES}}": "\n".join(groups),
        "{{POST_COUNT}}": str(len(posts)),
        "{{SERIES_COUNT}}": str(len(series)),
    }


def article_pages():
    d = _data()
    names = {s["id"]: s["name"] for s in d["series"]}
    pages = []
    for p in d["posts"]:
        if p.get("url"):
            continue
        body = (HERE / "posts" / f"{p['slug']}.html").read_text(encoding="utf-8")
        hero = (f'\n      <figure class="post__hero container" data-reveal><img src="{p["photo"]}" alt="" decoding="async" /></figure>' if p.get("photo") else "")
        by = f' · {escape(p["author"])}' if p.get("author") else ""
        pages.append((f"perspective-{p['slug']}.html", f'''  <main id="main" class="post-page">
    <article class="post" aria-labelledby="post-title">
      <header class="post__head container">
        <a class="post__back" href="perspectives.html">{BACK}Our Perspectives</a>
        <p class="eyebrow" data-reveal>{escape(names[p["series"]])} · {_date(p["date"])}{by}</p>
        <h1 class="post__title" id="post-title" data-reveal style="--i:1">{escape(p["title"])}</h1>
        <p class="post__lede" data-reveal style="--i:2">{escape(p["summary"])}</p>
      </header>{hero}
      <div class="post__body post__prose container">
{body}
      </div>
    </article>
  </main>''', p["summary"]))
    return pages

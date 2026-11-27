"""Cards for events.html and one post per event (event-<id>.html), from events.json. Called by tools/build.py."""
import json
import re
from html import escape as e
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 3.5v9M3.5 8h9"/></svg>'
BACK = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M10 3.5 5.5 8l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def events():
    return json.loads((HERE / "events.json").read_text(encoding="utf-8"))["past"]


def _text(s):
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a class="post__link" href="\2">\1</a>', e(s))


def _tags(x):
    tags = f'<span class="ev-mode ev-mode--{x["mode"]}">{x["mode"].capitalize()}</span>'
    return tags + (' <span class="ev-mode ev-mode--recurring">Recurring</span>' if x.get("recurring") else "")


def _card(i, x):
    fit = " ev-item__photo--whole" if x.get("fit") == "contain" else ""
    w, h = x["size"]
    return f'''          <li class="ev-item" id="{x["id"]}" data-mode="{x["mode"]}" data-reveal style="--i:{i % 3}">
            <img class="ev-item__photo{fit}" src="assets/events/{x["photo"]}.webp" alt="" width="{w}" height="{h}" loading="lazy" decoding="async" />
            <p class="ev-item__when">{e(x["when"])} <span class="ev-item__tags">{_tags(x)}</span></p>
            <h3 class="ev-item__title"><a href="event-{x["id"]}.html">{e(x["title"])}</a></h3>
            <p class="ev-item__place">{e(x["role"])} · {e(x["place"])}</p>
            <p class="ev-item__text">{e(x["text"])}</p>
            <span class="person__more ev-item__more" aria-hidden="true">Read the story {ARROW}</span>
          </li>'''


def render():
    return {"{{PAST_EVENTS}}": "\n".join(_card(i, x) for i, x in enumerate(events()))}


def _img(p, folder, lazy=True):
    w, h = p["size"]
    load = 'loading="lazy" ' if lazy else ""
    return f'<img src="assets/{folder}/{p["photo"]}.webp" alt="{e(p["alt"])}" width="{w}" height="{h}" {load}decoding="async" />'


def _block(b):
    out = f'          <section data-reveal><h2 class="ep-h">{e(b["h"])}</h2>'
    out += "".join(f"<p>{_text(t)}</p>" for t in b.get("p", []))
    if b.get("list"):
        out += '<ul role="list">' + "".join(f"<li>{_text(t)}</li>" for t in b["list"]) + "</ul>"
    return out + "</section>"


def post_page(x, nxt, *, prefix, folder, back, facts, tags=""):
    """<main> for one post. Also used for the team stories (tools/careers/render.py)."""
    p, gallery = x["post"], ""
    ph = p["photos"]
    for row in ([ph[:2], ph[2:]] if len(ph) == 4 else [ph] if ph else []):   # four photos make two rows
        items = "".join(f'<li style="--ratio:{f["size"][0] / f["size"][1]:.3f};--i:{k}" data-reveal>{_img(f, folder)}</li>' for k, f in enumerate(row))
        narrow = " ep-photos--narrow" if sum(f["size"][0] / f["size"][1] for f in row) < 2 else ""
        gallery += f'\n        <ul class="ep-photos{narrow}" role="list">{items}</ul>'
    hero = {"photo": x["photo"], "alt": x["alt"], "size": x["size"]}
    square = " ep-hero--square" if x["size"][0] <= x["size"][1] else ""
    rows = "\n".join(f"          <div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in facts)
    href, label = back
    return f'''  <main id="main" class="post-page">
    <article class="post ep" aria-labelledby="post-title">
      <header class="post__head container">
        <a class="post__back" href="{href}">{BACK}{label}</a>
        <p class="ep-when" data-reveal>{e(x["when"])} {tags}</p>
        <h1 class="post__title" id="post-title" data-reveal style="--i:1">{e(p["title"])}</h1>
        <p class="post__lede" data-reveal style="--i:2">{_text(p["lede"])}</p>
      </header>

      <figure class="post__hero ep-hero{square} container" data-reveal>{_img(hero, folder, lazy=False)}</figure>

      <div class="ep-body container">
        <dl class="ep-facts" data-reveal>
{rows}
        </dl>
        <div class="ep-text">
{chr(10).join(_block(b) for b in p["blocks"])}
        </div>
      </div>

      <div class="container">{gallery}
        <div class="post__close ep-close" data-reveal>
          <p class="post__quote">{e(p["close"])}</p>
          <div class="hero__ctas">
            <a class="btn" href="{e(p["cta"][1])}">{e(p["cta"][0])}</a>
            <a class="btn btn--ghost" href="{href}">{label}</a>
          </div>
          <a class="ep-next" href="{prefix}{nxt["id"]}.html"><span>Next</span>{e(nxt["post"]["title"])}</a>
        </div>
      </div>
    </article>
  </main>'''


def pages():
    """(output file, <main>, description, title) for each event post. Edit the text in events.json."""
    xs = events()
    for i, x in enumerate(xs):
        main = post_page(x, xs[(i + 1) % len(xs)], prefix="event-", folder="events", back=("events.html#past", "All events"),
                         facts=[("Event", x["title"]), ("Where", x["place"]), ("Our part", x["role"])], tags=f'<span class="ev-item__tags">{_tags(x)}</span>')
        yield f"event-{x['id']}.html", main, x["post"]["lede"], f"{x['post']['title']} | Earlyseed Ventures"

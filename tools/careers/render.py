"""Fills the {{…}} placeholders in tools/careers/main.html from openings.json, and builds the team stories (life-<id>.html) from stories.json.
Called by tools/team/build.py."""
import json
from html import escape as e
from pathlib import Path

HERE = Path(__file__).resolve().parent
EMPTY = '          <p class="lf-roles__none">We have no full-time roles open right now. When one opens, it will be listed here.</p>'


def _items(title, items):
    if not items:
        return ""
    return f'<div><h4>{title}</h4><ul role="list">{"".join(f"<li>{e(i)}</li>" for i in items)}</ul></div>'


def _role(o, careers):
    meta = " · ".join(e(o[k]) for k in ("team", "location", "type") if o.get(k))
    return f'''          <details class="lf-role">
            <summary><span class="lf-role__title">{e(o["title"])}</span><span class="lf-role__meta">{meta}</span><svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path d="M8 3v10M3 8h10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></summary>
            <div class="lf-role__body">
              <p>{e(o["summary"])}</p>
              <div class="lf-role__cols">{_items("What you will do", o.get("do"))}{_items("What we are looking for", o.get("bring"))}</div>
              <a class="btn lf-btn" href="{e(o.get("apply") or careers)}">Apply for this role</a>
            </div>
          </details>'''


def render():
    data = json.loads((HERE / "openings.json").read_text(encoding="utf-8"))
    roles = "\n".join(_role(o, data["careers"]) for o in data["openings"])
    return {"{{OPENINGS}}": roles or EMPTY, "{{INTERN_HREF}}": e(data["intern"])}


def pages(post_page):
    """(output file, <main>, description, title) for each team story. post_page comes from tools/events/render.py."""
    xs = json.loads((HERE / "stories.json").read_text(encoding="utf-8"))["stories"]
    for i, x in enumerate(xs):
        main = post_page(x, xs[(i + 1) % len(xs)], prefix="life-", folder="careers", back=("careers.html#life", "Life at Earlyseed"), facts=x["facts"])
        yield f"life-{x['id']}.html", main, x["post"]["lede"], f"{x['post']['title']} | Earlyseed Ventures"

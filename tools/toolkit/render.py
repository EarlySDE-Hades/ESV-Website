"""Tools for founders and investors, from tools/toolkit/tools.json. Called by tools/build.py.

  render() -> placeholders for tools/toolkit/main.html (tools.html, the hub)
  pages()  -> (output file, <main>, description, title) for each tool that is not 'soon'
"""
import json
from html import escape as e
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARROW = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M3 8h9.5M8.5 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
BACK = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M10 3.5 5.5 8l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# Small drawn icons in ESV colours, on a 64 x 64 box
ICONS = {
    "compass": '<circle cx="32" cy="32" r="24" fill="var(--crema)" stroke="var(--golden-glow)" stroke-width="4"/><path d="M32 14l7 18-7 18-7-18z" fill="var(--golden-glow)"/><path d="M32 14l7 18H25z" fill="var(--purple)"/><circle cx="32" cy="32" r="4" fill="#fff"/>',
    "scale": '<path d="M32 12v40M18 52h28" stroke="var(--bronze)" stroke-width="4" stroke-linecap="round"/><path d="M12 22h40" stroke="var(--golden-glow)" stroke-width="4" stroke-linecap="round"/><path d="M8 38l8-16 8 16z" fill="var(--sand)"/><path d="M40 34l8-12 8 12z" fill="var(--purple)"/><circle cx="32" cy="12" r="4" fill="var(--golden-glow)"/>',
    "layers": '<path d="M32 10 56 22 32 34 8 22z" fill="var(--purple)"/><path d="M8 32l24 12 24-12" fill="none" stroke="var(--golden-glow)" stroke-width="4" stroke-linejoin="round"/><path d="M8 42l24 12 24-12" fill="none" stroke="var(--bronze)" stroke-width="4" stroke-linejoin="round"/>',
    "hourglass": '<path d="M16 8h32M16 56h32" stroke="var(--bronze)" stroke-width="4" stroke-linecap="round"/><path d="M20 10c0 14 24 14 24 22S20 42 20 54h24c0-12-24-14-24-22S44 24 44 10z" fill="var(--crema)" stroke="var(--golden-glow)" stroke-width="3"/><path d="M24 52c2-6 14-6 16 0z" fill="var(--purple)"/><path d="M26 18h12c-2 4-10 4-12 0z" fill="var(--purple)"/>',
    "calendar": '<rect x="8" y="12" width="48" height="44" rx="8" fill="var(--crema)" stroke="var(--golden-glow)" stroke-width="4"/><path d="M8 26h48" stroke="var(--golden-glow)" stroke-width="4"/><path d="M20 6v12M44 6v12" stroke="var(--bronze)" stroke-width="4" stroke-linecap="round"/><rect x="16" y="34" width="8" height="8" rx="2" fill="var(--purple)"/><rect x="28" y="34" width="8" height="8" rx="2" fill="var(--purple)"/><rect x="40" y="34" width="8" height="8" rx="2" fill="var(--pastel-purple)"/><rect x="16" y="46" width="8" height="6" rx="2" fill="var(--pastel-purple)"/>',
    "steps": '<rect x="8" y="40" width="14" height="16" rx="3" fill="var(--sand)"/><rect x="25" y="28" width="14" height="28" rx="3" fill="var(--bronze)"/><rect x="42" y="12" width="14" height="44" rx="3" fill="var(--purple)"/>',
    "pool": '<ellipse cx="32" cy="40" rx="24" ry="12" fill="var(--sand)"/><circle cx="22" cy="30" r="6" fill="var(--purple)"/><circle cx="34" cy="26" r="6" fill="var(--golden-glow)"/><circle cx="44" cy="32" r="6" fill="var(--bronze)"/>',
    "growth": '<path d="M8 50l14-14 10 8 22-24" fill="none" stroke="var(--golden-glow)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M42 18h14v14" fill="none" stroke="var(--purple)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
    "slice": '<circle cx="30" cy="34" r="20" fill="var(--sand)"/><path d="M30 34V14a20 20 0 0 1 20 20z" fill="var(--golden-glow)"/><path d="M36 28V8a20 20 0 0 1 20 20z" fill="var(--purple)"/>',
}


def tools():
    return json.loads((HERE / "tools.json").read_text(encoding="utf-8"))["tools"]


def icon(name, size=56):
    return f'<svg class="tk-icon" viewBox="0 0 64 64" width="{size}" height="{size}" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def _card(t, i):
    if t.get("soon"):
        return f'''            <li class="tk-card tk-card--soon" data-reveal style="--i:{i % 3}">
              {icon(t["icon"])}
              <h3 class="tk-card__name">{e(t["name"])}</h3>
              <p class="tk-card__sum">{e(t["summary"])}</p>
              <span class="tk-card__soon">Coming soon</span>
            </li>'''
    return f'''            <li class="tk-card" data-reveal style="--i:{i % 3}">
              <a class="tk-card__link" href="tool-{t["slug"]}.html">
                {icon(t["icon"])}
                <h3 class="tk-card__name">{e(t["name"])}</h3>
                <p class="tk-card__sum">{e(t["summary"])}</p>
                <span class="tk-card__go">Open the tool {ARROW}</span>
              </a>
            </li>'''


def render():
    ts = tools()
    out = {}
    for who in ("founders", "investors"):
        out["{{" + who.upper() + "}}"] = "\n".join(_card(t, i) for i, t in enumerate(x for x in ts if x["for"] == who))
    return out


def pages():
    ts = [t for t in tools() if not t.get("soon")]
    for n, t in enumerate(ts):
        body = (HERE / "pages" / f"{t['slug']}.html").read_text(encoding="utf-8").rstrip()
        reads = "".join(f'<li><a href="{h}">{e(title)} {ARROW}</a></li>' for title, h in t["read"])
        nxt = ts[(n + 1) % len(ts)]
        main = f'''  <main id="main" class="post-page tk-page">
    <article aria-labelledby="tk-title">
      <header class="post__head container">
        <a class="post__back" href="tools.html">{BACK}All tools</a>
        <span class="tk-head__icon" data-reveal>{icon(t["icon"], 64)}</span>
        <p class="eyebrow" data-reveal>Tools for {t["for"]}</p>
        <h1 class="post__title" id="tk-title" data-reveal style="--i:1">{e(t["name"])}</h1>
        <p class="post__lede" data-reveal style="--i:2">{e(t["lede"])}</p>
      </header>
      <div class="container tk-wrap">
        <p class="tk-disclaimer" role="note"><svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 7v4.2M8 4.6v.1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><span><strong>Indicative only, and not financial advice. Always check with a legal advisor before you sign anything.</strong> These numbers are an illustration to help you think.</span></p>
{body}
        <p class="tk-note"><strong>Indicative only, and not financial advice. Always check with a legal advisor before you sign anything.</strong> These tools are an illustration, not financial, legal or tax advice, and they simplify real term sheets. Check your numbers with your CA, and your documents with a legal advisor, before you rely on them. Nothing you enter leaves your browser.</p>
        <div class="tk-after">
          {f'<div><h2 class="tk-after__h">Read the article</h2><ul role="list" class="tk-after__list">{reads}</ul></div>' if reads else ''}
          <div><h2 class="tk-after__h">Next tool</h2><ul role="list" class="tk-after__list"><li><a href="tool-{nxt["slug"]}.html">{e(nxt["name"])} {ARROW}</a></li></ul></div>
          <div><h2 class="tk-after__h">Want a second opinion?</h2><p class="tk-after__p">Prologue works with founders before they raise: the deck, the model and the story.</p><a class="btn" href="prologue.html">Explore Prologue</a></div>
        </div>
      </div>
    </article>
  </main>'''
        yield f"tool-{t['slug']}.html", main, t["summary"], f"{t['seo']} | Earlyseed Ventures"

"""Render the Bootcamps page's campus partners from the #partner-data JSON in index.html
(the same data the home page's campus strip uses), and the campus logo cards from the About page. Called by tools/build.py."""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXT = '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M6 3.5h6.5V10M12.5 3.5 4 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def render():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    partners = json.loads(re.search(r'<script type="application/json" id="partner-data">([\s\S]*?)</script>', index).group(1))
    # logo sizes as used in the home page strip
    sizes = dict(re.findall(r'src="assets/logos/campus/([\w-]+)\.webp" alt="[^"]*" (width="\d+" height="\d+")', index))
    rows = []
    for n, p in enumerate(partners):
        logo = f'<img src="assets/logos/campus/{p["slug"]}.webp" alt="" {sizes.get(p["slug"], "")} loading="lazy" decoding="async" />'
        meta = " · ".join(filter(None, [p.get("sector"), p.get("location"), f'Est. {p["founded"]}' if p.get("founded") else None]))
        site = ""
        if p.get("website"):
            host = p["website"].split("//", 1)[-1].split("/", 1)[0].removeprefix("www.")
            site = (f'<a class="bc-partner__site" href="{escape(p["website"])}" target="_blank" rel="noopener noreferrer" '
                    f'aria-label="{escape(p["name"])} website (opens in a new tab)">{escape(host)} {EXT}</a>')
        reveal = f' style="--i:{n % 2}"' if n % 2 else ""
        rows.append(f'''          <li class="bc-partner" id="{p["slug"]}" data-reveal{reveal}>
            <div class="bc-partner__logo">{logo}</div>
            <div class="bc-partner__text">
              <h3 class="bc-partner__name">{escape(p["name"])}</h3>
              <p class="bc-partner__meta">{escape(meta)}</p>
              <p class="bc-partner__summary">{escape(p["summary"])}</p>
              {site}
            </div>
          </li>''')
    # the same logo cards as About's "On campus" section
    about = (ROOT / "tools/about/main.html").read_text(encoding="utf-8")
    campus = re.search(r'        <ul class="campus-grid"[\s\S]*?</ul>', about).group(0)
    return {"{{CAMPUS}}": campus, "{{PARTNERS}}": "\n".join(rows), "{{PARTNER_COUNT}}": str(len(partners))}

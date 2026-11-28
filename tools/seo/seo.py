"""Search tags for every page: title, description, canonical link, link-preview tags and structured data,
plus sitemap.xml and robots.txt. Called by tools/build.py.

The tags live between the <!-- seo --> and <!-- /seo --> comments in each page's <head>, index.html included.
Change the wording here (TITLES, HOME_DESCRIPTION), not in the pages. If the domain changes, change SITE.
"""
import importlib.util
import json
import re
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://www.earlyseedventures.com"
BRAND = "Earlyseed Ventures"
HOME_DESCRIPTION = "A Mumbai-based boutique investment bank helping India’s high-potential start-ups raise seed to Series A, and giving investors an early seat at the table."
TITLES = {
    "index.html": "Earlyseed Ventures | Boutique Investment Bank in Mumbai",
    "about.html": "About Us: How We Work | Earlyseed Ventures",
    "team.html": "Our Team and Leadership | Earlyseed Ventures",
    "portfolio.html": "Our Portfolio of Indian Start-ups | Earlyseed Ventures",
    "perspectives.html": "Our Perspectives on Fundraising | Earlyseed Ventures",
    "press.html": "Us in the News: Press Coverage | Earlyseed Ventures",
    "bootcamps.html": "Founder Bootcamps on Campus | Earlyseed Ventures",
    "events.html": "Events for Founders and Investors | Earlyseed Ventures",
    "event-seed-to-success.html": "From Seed to Success: Event Recap | Earlyseed Ventures",
    "invest.html": "Invest With Us: Syndicate and Partners | Earlyseed Ventures",
    "careers.html": "Careers: Life at Earlyseed and Openings | Earlyseed Ventures",
    "prologue.html": "Prologue: Fundraising Prep for Founders | Earlyseed Ventures",
    "tools.html": "Free Fundraising Tools for Founders | Earlyseed Ventures",
    "404.html": "Page Not Found | Earlyseed Ventures",
}
# breadcrumb: the page's own name, and its parent page if it isn't directly under Home
CRUMBS = {
    "about.html": ("About", None), "team.html": ("Team", None), "portfolio.html": ("Our Portfolio", None),
    "perspectives.html": ("Our Perspectives", None), "press.html": ("Our Press", None), "bootcamps.html": ("Bootcamps", None),
    "events.html": ("Events", None), "event-seed-to-success.html": ("From seed to success", "events.html"), "prologue.html": ("Prologue", None), "invest.html": ("Invest with us", None), "careers.html": ("Careers", None),
    "tools.html": ("Tools", "perspectives.html"),
}
TYPES = {"about.html": "AboutPage", "portfolio.html": "CollectionPage", "press.html": "CollectionPage", "perspectives.html": "CollectionPage", "events.html": "CollectionPage"}
ORG = f"{SITE}/#organization"


def url(page):
    """Public address of a page: Vercel serves clean URLs (vercel.json "cleanUrls"), so no .html."""
    return f"{SITE}/" if page == "index.html" else f"{SITE}/{page.removesuffix('.html')}"


def short(text, limit=158):
    """Search results cut descriptions at about 160 characters: end on a sentence if one fits, else on a word."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    end = max((m.end() for m in re.finditer(r"[.!?](?=\s)", text) if m.end() <= limit), default=0)
    if end >= 90:
        return text[:end]
    return text[: text.rindex(" ", 0, limit)].rstrip(",;: ") + "…"


def _companies():
    cs = json.loads((ROOT / "tools/portfolio/companies.json").read_text(encoding="utf-8"))["companies"]
    return {f"portfolio-{c['slug']}.html": c for c in cs}


def _events():
    xs = json.loads((ROOT / "tools/events/events.json").read_text(encoding="utf-8"))["past"]
    return {f"event-{x['id']}.html": x["title"] for x in xs}


def _originals():
    xs = json.loads((ROOT / "tools/perspectives/posts.json").read_text(encoding="utf-8"))["posts"]
    return {f"perspective-{x['slug']}.html": x["original"] for x in xs if x.get("original") and not x.get("url")}


def _posts():
    """Articles hosted on this site, with their series name: perspective-<slug>.html -> post."""
    d = json.loads((ROOT / "tools/perspectives/posts.json").read_text(encoding="utf-8"))
    names = {s["id"]: s["name"] for s in d["series"]}
    return {f"perspective-{x['slug']}.html": {**x, "series_name": names.get(x["series"])}
            for x in d["posts"] if not x.get("url") and not x.get("original")}


def _authors():
    spec = importlib.util.spec_from_file_location("perspectives_render", ROOT / "tools/perspectives/render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.AUTHORS


def _tools():
    xs = json.loads((ROOT / "tools/toolkit/tools.json").read_text(encoding="utf-8"))["tools"]
    return {f"tool-{x['slug']}.html": x for x in xs if not x.get("soon")}


def _article(page, post, title):
    """Article markup: headline, dates, author and publisher, so search engines can credit the writer."""
    d = {"@type": "BlogPosting", "@id": f"{url(page)}#article", "headline": title.split(" | ")[0], "description": post["summary"],
         "datePublished": post["date"], "dateModified": post.get("updated", post["date"]),
         "image": f"{SITE}/assets/perspectives/{post['photo']}" if post.get("photo") else f"{SITE}/assets/brand/og.jpg",
         "mainEntityOfPage": {"@id": url(page)}, "publisher": {"@type": "Organization", "@id": ORG, "name": BRAND, "url": f"{SITE}/",
         "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/brand/icons/icon-512.png"}}, "inLanguage": "en-IN"}
    if post.get("series_name"):
        d["articleSection"] = post["series_name"]
    if post.get("words"):
        d["wordCount"] = post["words"]
    authors = _authors()
    if post.get("author") in authors:
        role, photo, link = authors[post["author"]]
        link = link.split("#")[0]
        a = {"@type": "Person", "name": post["author"], "jobTitle": role, "image": f"{SITE}/{photo}", "url": url(link),
             "worksFor": {"@type": "Organization", "@id": ORG, "name": BRAND}}
        if link.startswith("team-"):
            a["@id"] = f"{url(link)}#person"
        d["author"] = a
    else:
        d["author"] = {"@type": "Organization", "@id": ORG, "name": BRAND, "url": f"{SITE}/"}
    return d


def _stories():
    xs = json.loads((ROOT / "tools/careers/stories.json").read_text(encoding="utf-8"))["stories"]
    return {f"life-{x['id']}.html": x["post"]["title"] for x in xs}


def _people():
    spec = importlib.util.spec_from_file_location("profiles", ROOT / "tools/team/profiles.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {p["page"]: p for p in mod.people()}


def _person(p):
    d = {"@type": "Person", "@id": f"{url(p['page'])}#person", "name": p["name"], "url": url(p["page"]), "jobTitle": p["role"],
         "image": f"{SITE}/assets/team/{p['slug']}.webp", "description": p["bio"]}
    if p["group"] == "leadership":
        d["worksFor"] = {"@type": "Organization", "@id": ORG, "name": BRAND, "url": f"{SITE}/"}
    if p["prefix"]:
        d["honorificPrefix"] = p["prefix"]
    if p["linkedin"]:
        d["sameAs"] = [p["linkedin"]]
    if p["affiliations"]:
        d["affiliation"] = [{"@type": "Organization", "name": a} for a, _ in p["affiliations"]]
    return d


def _organization(people):
    return {
        "@type": "Organization", "@id": ORG, "name": BRAND, "legalName": "Earlyseed Ventures Pvt. Ltd.", "url": f"{SITE}/",
        "logo": f"{SITE}/assets/brand/icons/icon-512.png", "image": f"{SITE}/assets/brand/og.jpg", "description": HOME_DESCRIPTION,
        "email": "info@earlyseedventures.com", "telephone": "+91 22 4513 3786",
        "address": {"@type": "PostalAddress", "streetAddress": "3, Enterprise Centre, Near Orchid Hotel, Vile Parle (E)",
                    "addressLocality": "Mumbai", "addressRegion": "Maharashtra", "postalCode": "400099", "addressCountry": "IN"},
        "areaServed": "IN", "sameAs": ["https://www.linkedin.com/company/earlyseed-ventures"],
        "founder": [{"@type": "Person", "@id": f"{url(p['page'])}#person", "name": p["name"], "jobTitle": p["role"], "url": url(p["page"])}
                    for p in people.values() if p["role"].startswith("Co-founder")],
    }


def _crumbs(page, companies, people, title=None):
    if page in companies:
        chain = [("Home", "index.html"), ("Our Portfolio", "portfolio.html"), (companies[page]["name"], page)]
    elif page in people:
        chain = [("Home", "index.html"), ("Team", "team.html"), (people[page]["name"], page)]
    elif page in _events():
        chain = [("Home", "index.html"), ("Events", "events.html"), (_events()[page], page)]
    elif page in _stories():
        chain = [("Home", "index.html"), ("Careers", "careers.html"), (_stories()[page], page)]
    elif page.startswith("perspective-"):
        chain = [("Home", "index.html"), ("Our Perspectives", "perspectives.html"), (title.split(" | ")[0] if title else page, page)]
    elif page.startswith("tool-"):
        chain = [("Home", "index.html"), ("Tools", "tools.html"), (title.split(" | ")[0] if title else page, page)]
    elif page in CRUMBS:
        name, parent = CRUMBS[page]
        chain = [("Home", "index.html")] + ([(CRUMBS[parent][0], parent)] if parent else []) + [(name, page)]
    else:
        return None
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": url(p)} for i, (n, p) in enumerate(chain, 1)]}


def block(page, description, title=None):
    companies, people = _companies(), _people()
    c, person = companies.get(page), people.get(page)
    post, tool = _posts().get(page), _tools().get(page)
    if person:
        title = f"{person['name']}, {person['role']} | {BRAND}"
        if len(title) > 65:
            role = person["role"].removeprefix("Co-founder and ") if person["group"] == "leadership" else "Strategic Growth Partner"
            title = f"{person['name']}, {role} | {BRAND}"
        if len(title) > 70:
            title = f"{person['name']} | {BRAND}"
    if c:
        title = f"{c['name']}: {c.get('tag') or c['sector']} | {BRAND}"
        if len(title) > 62:
            title = f"{c['name']} | {BRAND}"
    title = title or TITLES.get(page)
    assert title, f"no title for {page}: add it to TITLES in tools/seo/seo.py"
    description = short(HOME_DESCRIPTION if page == "index.html" else description)
    graph = []
    if page == "index.html":
        graph += [_organization(people), {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": BRAND, "publisher": {"@id": ORG}, "inLanguage": "en-IN"}]
    else:
        web = {"@type": TYPES.get(page, "WebPage"), "@id": url(page), "url": url(page), "name": title.split(" | ")[0], "description": description,
               "isPartOf": {"@type": "WebSite", "@id": f"{SITE}/#website", "name": BRAND, "url": f"{SITE}/"},
               "publisher": {"@type": "Organization", "@id": ORG, "name": BRAND, "url": f"{SITE}/"}, "inLanguage": "en-IN"}
        if page == "about.html":
            web["about"] = _organization(people)
            del web["publisher"]
        if c:
            web["about"] = {k: v for k, v in {"@type": "Organization", "name": c["name"], "url": c.get("website"), "description": c["short"]}.items() if v}
        if page == "portfolio.html":
            web["mainEntity"] = {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i, "name": x["name"], "url": url(p)} for i, (p, x) in enumerate(companies.items(), 1)]}
        graph.append(web)
        if page == "team.html":
            web["mainEntity"] = {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i, "name": x["name"], "url": url(p)} for i, (p, x) in enumerate(people.items(), 1)]}
        if post:
            graph.append(_article(page, post, title))
        if tool:
            web["mainEntity"] = {"@type": "WebApplication", "name": title.split(" | ")[0], "description": tool["summary"],
                                 "url": url(page), "applicationCategory": "FinanceApplication", "operatingSystem": "Any",
                                 "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
                                 "provider": {"@type": "Organization", "@id": ORG, "name": BRAND}}
        if person:
            web["@type"] = "ProfilePage"
            web["mainEntity"] = _person(person)
            graph += [{"@type": "Book", "name": b, "author": {"@id": web["mainEntity"]["@id"]}} for b in person["books"]]
        crumbs = _crumbs(page, companies, people, title)
        if crumbs:
            graph.append(crumbs)
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    e = lambda s: escape(s, quote=True)
    og_type = "article" if post else "website"
    published = f'\n  <meta property="article:published_time" content="{post["date"]}" />' if post else ""
    if page == "404.html":
        # Served at whatever address was missing (build.py makes its links start at the site root); never indexed
        return f'''<!-- seo -->
  <!-- Written by tools/seo/seo.py (python tools/build.py): change it there. -->
  <title>{escape(title, quote=False)}</title>
  <meta name="robots" content="noindex" />
  <!-- /seo -->'''
    return f'''<!-- seo -->
  <!-- Written by tools/seo/seo.py (python tools/build.py): change it there. -->
  <title>{escape(title, quote=False)}</title>
  <meta name="description" content="{e(description)}" />
  <link rel="canonical" href="{_originals().get(page, url(page))}" />
  <meta property="og:type" content="{og_type}" />{published}
  <meta property="og:site_name" content="{BRAND}" />
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(description)}" />
  <meta property="og:url" content="{url(page)}" />
  <meta property="og:image" content="{SITE}/assets/brand/og.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <script type="application/ld+json">{data}</script>
  <!-- /seo -->'''


def apply(html, page, description, title=None):
    new = block(page, description, title)
    html, n = re.subn(r"<!-- seo -->[\s\S]*?<!-- /seo -->", lambda m: new, html, count=1)
    assert n == 1, f"no <!-- seo --> block in {page}"
    return html


def write_sitemap(pages):
    posts = _posts()
    lastmod = lambda p: f"<lastmod>{posts[p].get('updated', posts[p]['date'])}</lastmod>" if p in posts else ""
    rows = "\n".join(f"  <url><loc>{url(p)}</loc>{lastmod(p)}</url>" for p in pages if p not in _originals() and p != "404.html")
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n', encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8", newline="\n")

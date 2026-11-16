#!/usr/bin/env python3
"""Builds the static site from src/content/*.md and src/data/*.json into the repository root.

Usage:  pip install markdown   then   python3 src/build.py
"""
import datetime, html, json, pathlib, re
import markdown

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
# Public address of the site. Change this one line if the repository or account is renamed.
SITE_URL = "https://mzeeshan-phd.github.io"
SITE_TITLE = "Muhammad Zeeshan"
NAV = [("Home", "/"), ("Research", "/research/"), ("Publications", "/publications/"),
       ("Funding and Projects", "/funding/"), ("Teaching", "/teaching/"),
       ("Leadership and Service", "/service/"), ("CV", "/cv/")]
PAGES = ["index", "research", "publications", "funding", "teaching", "service", "cv", "group", "news"]
# Old addresses that now point somewhere else.
REDIRECTS = {"/awards/": "/cv/", "/services/": "/service/", "/contact/": "/"}

# Key numbers on the home page.
STATS = [("40", "peer-reviewed papers"), ("1,280", "citations"), ("16", "h-index"),
         ("10", "MS theses supervised"), ("4 yrs", "industry R&D as PI")]
# Latest items on the home page; the full list is in content/news.md.
HOME_NEWS = [
    ("Nov 2026", "Two papers accepted at IEEE ICoDT2 2026, Islamabad"),
    ("Feb 2026", "Two papers published at ICACS 2026, Lahore"),
    ("2026", "MoHERI research grant approved: Secure Internet of Medical Things Infrastructures for Smart Healthcare (Co-Principal Investigator, 2026 – 2028)"),
    ("Sep 2025", "Joined Sohar University, Oman, as Associate Professor"),
    ("May 2025", "Two papers published at AIIT 2025"),
    ("2025", "Article published in the Journal of the Franklin Institute"),
    ("2025", "Article published in Algorithms"),
    ("2025", "Paper published at IEEE HONET 2025"),
]
# Research students supervised by the site owner, marked with * in author lists.
STUDENTS = ["M. A. Bilal", "M. Luqman", "C. Tanzeel", "Z. Rihan"]

PUBS = json.loads((SRC / "data" / "publications.json").read_text(encoding="utf-8"))


def esc(s):
    return html.escape(s, quote=False)


def authors_html(a):
    a = esc(a)
    for s in STUDENTS:
        a = re.sub(r"(?<![A-Z]\. )\b" + re.escape(s) + r"\b", s + "*", a)
    return a.replace("M. Zeeshan", "<u>M. Zeeshan</u>")


def pub_row(p, show_citations=False):
    label = f"{esc(p['label'])} ’{str(p['year'])[2:]}"
    venue = esc(p["venue"]) + (", " + esc(p["details"]) if p.get("details") else "")
    tags = ""
    if p.get("status") == "accepted":
        tags += '<span class="tag">accepted</span>'
    if show_citations and p.get("citations"):
        tags += f'<span class="tag">cited {p["citations"]} times</span>'
    link = f' &middot; <a href="https://doi.org/{p["doi"]}">doi</a>' if p.get("doi") else ""
    return (f'<tr><td class="v">{label}</td><td><span class="t">{esc(p["title"])}</span>{tags}'
            f'<span class="a">{authors_html(p["authors"])}</span>'
            f'<span class="d">{venue}{link}</span></td></tr>')


def selected_html():
    sel = [p for p in PUBS if p.get("selected")]
    sel.sort(key=lambda p: (p["type"] != "journal", -p["citations"]))
    return '<table class="pubs">' + "".join(pub_row(p, True) for p in sel) + "</table>"


def publist_html():
    rows, year = [], None
    for p in sorted(PUBS, key=lambda p: (-p["year"], p["type"] != "journal")):
        if p["year"] != year:
            year = p["year"]
            rows.append(f'<tr class="yr"><td colspan="2">{year}</td></tr>')
        rows.append(pub_row(p))
    return '<table class="pubs">' + "".join(rows) + "</table>"


def blocks():
    stats = '<div class="stats">' + "".join(
        f"<div><b>{esc(n)}</b><span>{esc(t)}</span></div>" for n, t in STATS) + "</div>"
    news = '<ul class="news">' + "".join(
        f"<li><i>{esc(d)}</i>{esc(t)}</li>" for d, t in HOME_NEWS) + "</ul>"
    return {"STATS": stats, "NEWS": news, "SELECTED": selected_html(), "PUBLIST": publist_html()}


JSONLD = {
    "@context": "https://schema.org", "@type": "Person", "name": "Muhammad Zeeshan",
    "honorificSuffix": "PhD, SMIEEE", "jobTitle": "Associate Professor", "url": SITE_URL + "/",
    "image": SITE_URL + "/images/profile.jpg", "email": "mailto:muhammad.zeeshan@ieee.org",
    "worksFor": {"@type": "CollegeOrUniversity", "name": "Sohar University",
                 "address": {"@type": "PostalAddress", "addressLocality": "Sohar", "addressCountry": "OM"}},
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "National University of Sciences and Technology (NUST)"},
    "knowsAbout": ["Network security", "Intrusion detection", "Internet of Things security",
                   "Phishing detection", "Machine learning", "Computer networks"],
    "sameAs": ["https://scholar.google.com.pk/citations?user=bIB6sP4AAAAJ&hl=en",
               "https://orcid.org/0000-0003-4417-1365",
               "https://www.scopus.com/authid/detail.uri?authorId=57214970753",
               "https://www.linkedin.com/in/zeeshanbhatti/"],
}


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines())
    return meta, m.group(2)


def relativise(page, url):
    # Internal links are written as "/path" and made relative here, so the site works
    # at any address. The 404 page gets full addresses.
    if url == "/404.html":
        prefix = SITE_URL + "/"
    else:
        prefix = "./" if url == "/" else "../"
    return re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{prefix}', page)


def render(meta, body_html, today):
    url = meta["permalink"]
    nav = "\n".join('<a href="%s"%s>%s</a>' % (u, ' class="on"' if url == u else "", esc(t)) for t, u in NAV)
    title = meta["title"]
    full_title = "Muhammad Zeeshan, PhD, SMIEEE" if url == "/" else f"{title} - {SITE_TITLE}"
    jsonld = ('<script type="application/ld+json">' + json.dumps(JSONLD) + "</script>") if url == "/" else ""
    page = (SRC / "layout.html").read_text(encoding="utf-8").format(
        full_title=html.escape(full_title), title=html.escape(title),
        description=html.escape(meta.get("description", "")), canonical=SITE_URL + url, nav=nav,
        content=body_html, year=today.year, updated_human=today.strftime("%B %Y"),
        site_url=SITE_URL, jsonld=jsonld)
    return relativise(page, url)


def main():
    today = datetime.date.today()
    urls, blk = [], blocks()
    for name in PAGES:
        meta, body = parse(SRC / "content" / f"{name}.md")
        body_html = markdown.markdown(body, extensions=["tables", "attr_list", "sane_lists", "smarty"])
        for k, v in blk.items():
            body_html = body_html.replace("<p>{{%s}}</p>" % k, v)
        assert "{{" not in body_html, name
        body_html = re.sub(r"<table>.*?</table>", lambda m: '<div class="table-scroll">' + m.group(0) + "</div>",
                           body_html, flags=re.S)
        out = ROOT / meta["permalink"].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(meta, body_html, today), encoding="utf-8")
        urls.append(meta["permalink"])
    meta = {"title": "Page Not Found", "permalink": "/404.html", "description": "Page not found."}
    (ROOT / "404.html").write_text(
        render(meta, '<p>Sorry, that page does not exist. Return to the <a href="/">home page</a>.</p>', today),
        encoding="utf-8")
    for old, new in REDIRECTS.items():
        d = ROOT / old.strip("/")
        d.mkdir(parents=True, exist_ok=True)
        target = SITE_URL + new
        (d / "index.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{target}">'
            f'<meta http-equiv="refresh" content="0; url={target}"><p>This page has moved to <a href="{target}">{target}</a>.</p>\n')
    sm = "".join(f"<url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    (ROOT / ".nojekyll").write_text("")
    print("Built", len(urls), "pages")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Builds the static site from src/content/*.md into the repository root.

Usage:  pip install markdown   then   python3 src/build.py
Styling comes from the AcademicPages template (MIT licence, see LICENSE-AcademicPages).
"""
import datetime, html, pathlib, re
import markdown

SRC = pathlib.Path(__file__).resolve().parent
ROOT = SRC.parent
SITE_URL = "https://mzeeshanbhatti.github.io"
SITE_TITLE = "Muhammad Zeeshan"
NAV = [("Publications", "/publications/"), ("Research", "/research/"), ("Teaching", "/teaching/"),
       ("Services", "/services/"), ("Awards", "/awards/"),
       ("CV", "/cv/"), ("Contact", "/contact/")]
PAGES = ["index", "publications", "research", "teaching", "services", "awards", "cv", "contact"]


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines())
    return meta, m.group(2)


def render(meta, body_html, today):
    url = meta["permalink"]
    nav = "\n".join(
        f'          <li class="masthead__menu-item{" selected" if url == u else ""}"><a href="{u}">{t}</a></li>'
        for t, u in NAV)
    title = meta["title"]
    full_title = SITE_TITLE if url == "/" else f"{title} - {SITE_TITLE}"
    return (SRC / "layout.html").read_text(encoding="utf-8").format(
        full_title=html.escape(full_title), title=html.escape(title),
        description=html.escape(meta.get("description", "")),
        canonical=SITE_URL + url, nav=nav, home_selected=" selected" if url == "/" else "",
        content=body_html, year=today.year, updated=today.isoformat(), site_title=SITE_TITLE)


def main():
    today = datetime.date.today()
    urls = []
    for name in PAGES:
        meta, body = parse(SRC / "content" / f"{name}.md")
        body_html = markdown.markdown(body, extensions=["tables", "attr_list", "sane_lists", "smarty"])
        out = ROOT / meta["permalink"].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(meta, body_html, today), encoding="utf-8")
        urls.append(meta["permalink"])
    meta = {"title": "Page Not Found", "permalink": "/404.html", "description": "Page not found."}
    (ROOT / "404.html").write_text(
        render(meta, '<p>Sorry, that page does not exist. Return to the <a href="/">home page</a>.</p>', today),
        encoding="utf-8")
    sm = "".join(f"<url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    (ROOT / ".nojekyll").write_text("")
    print("Built", len(urls), "pages")


if __name__ == "__main__":
    main()

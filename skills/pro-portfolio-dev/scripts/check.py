#!/usr/bin/env python3
"""Check a built portfolio before publishing. Read-only, no network.

  python3 check.py site/        prints one line per check, then PASS or FAIL (exit 1)

Checks: the files exist, SEO and share tags, JSON-LD parses, sitemap and canonical agree, og.png is 1200x630,
every <img> has alt, html has lang, no external scripts or stylesheets, every UI language has every key,
page weight under 150 KB.
"""
import html.parser
import json
import pathlib
import re
import struct
import sys

FILES = ("index.html", "robots.txt", "sitemap.xml", "llms.txt", "favicon.svg", "og.png", ".nojekyll")
TAGS = ("description", "og:title", "og:description", "og:image", "og:url", "twitter:card")
MAX_KB = 150


class Scan(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta, self.imgs_no_alt, self.external, self.lang, self.canon = {}, 0, [], None, None
        self.ld, self.i18n, self._grab = [], "", None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "meta" and a.get("content") is not None:
            self.meta[a.get("name") or a.get("property")] = a["content"]
        elif tag == "img" and not a.get("alt"):
            self.imgs_no_alt += 1
        elif tag == "script" and a.get("src", "").startswith(("http", "//")):
            self.external.append(a["src"])
        elif tag == "link" and a.get("rel") == "stylesheet" and a.get("href", "").startswith(("http", "//")):
            self.external.append(a["href"])
        elif tag == "link" and a.get("rel") == "canonical":
            self.canon = a.get("href")
        if tag == "script":
            self._grab = {"application/ld+json": "ld"}.get(a.get("type"), "i18n" if a.get("id") == "i18n" else None)

    def handle_endtag(self, tag):
        if tag == "script":
            self._grab = None

    def handle_data(self, data):
        if self._grab == "ld":
            self.ld.append(data)
        elif self._grab == "i18n":
            self.i18n += data


def png_size(p: pathlib.Path) -> tuple:
    head = p.read_bytes()[:24]
    return struct.unpack(">II", head[16:24]) if head[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)


def i18n_check(raw: str) -> tuple:
    """Every language in the page's UI table has the same keys. Sites not built by build.py have no table."""
    name = "every language has every UI key"
    if not raw.strip():
        return (name + " (no i18n table)", True)
    try:
        ui = json.loads(raw)["ui"]
        keys = set(ui["en"])
        return (name, all(set(v) == keys for v in ui.values()))
    except (ValueError, KeyError):
        return (name, False)


def run(site: pathlib.Path) -> list:
    res = [(f"file {f}", (site / f).exists()) for f in FILES]
    idx = site / "index.html"
    if not idx.exists():
        return res
    page = idx.read_text(encoding="utf-8")
    s = Scan()
    s.feed(page)
    res += [(f"meta {t}", bool(s.meta.get(t))) for t in TAGS]
    res.append(("<title>", bool(re.search(r"<title>[^<]{10,}</title>", page))))
    res.append(("html lang", bool(s.lang)))
    res.append(("canonical https", bool(s.canon and s.canon.startswith("https://"))))
    try:
        ok = all(json.loads(x) for x in s.ld) and bool(s.ld)
    except ValueError:
        ok = False
    res.append(("JSON-LD parses", ok))
    sm = (site / "sitemap.xml").read_text(encoding="utf-8") if (site / "sitemap.xml").exists() else ""
    res.append(("sitemap lists canonical", bool(s.canon) and f"<loc>{s.canon}</loc>" in sm))
    res.append(("og.png 1200x630", (site / "og.png").exists() and png_size(site / "og.png") == (1200, 630)))
    res.append(("every img has alt", s.imgs_no_alt == 0))
    res.append(("no external scripts/styles", not s.external))
    res.append(i18n_check(s.i18n))
    kb = idx.stat().st_size / 1024
    res.append((f"page weight {kb:.0f} KB <= {MAX_KB}", kb <= MAX_KB))
    return res


def main() -> None:
    site = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    res = run(site)
    for name, ok in res:
        print(("ok   " if ok else "FAIL ") + name)
    bad = sum(not ok for _, ok in res)
    print(f"{'PASS' if not bad else 'FAIL'} {len(res) - bad}/{len(res)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

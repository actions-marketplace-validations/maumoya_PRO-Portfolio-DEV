#!/usr/bin/env python3
"""Build a one-page portfolio site from repos.json (fetch.py) and plan.json (written by the agent).

  python3 build.py repos.json plan.json --out site/

Writes only inside --out: index.html (CSS and JS inlined, no external requests), og.png (1200x630,
needs Pillow; skipped with a warning without it), favicon.svg, robots.txt, sitemap.xml, llms.txt, .nojekyll.
Every project in the plan must be a real repo in repos.json; stars, language and dates come from GitHub only.
"""
import argparse
import datetime
import html
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
THEMES = ("auto", "light", "dark", "ocean", "forest", "sunset", "mono", "contrast")
e = html.escape


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(plan: dict, repos: dict) -> list:
    errs = [f"plan.json is missing '{k}'" for k in ("name", "url", "headline", "tagline", "projects") if not plan.get(k)]
    if not str(plan.get("url", "")).startswith("https://"):
        errs.append("url must be the live https:// address (used for canonical, sitemap and share tags)")
    for p in plan.get("projects", []):
        if p.get("repo") not in repos:
            errs.append(f"project '{p.get('repo')}' is not a repo in repos.json (never invent projects)")
    return errs


def ui_table() -> tuple:
    u = load(HERE / "ui.json")
    keys, names = u["_keys"], u["_names"]
    return {l: dict(zip(keys, u[l])) for l in names}, names


def card(p: dict, r: dict, en: dict) -> str:
    name = r["name"]
    title = p.get("title") or name
    url = r["html_url"]
    live = p.get("demo") or r.get("homepage") or ""
    tags = p.get("tags") or (r.get("topics") or [])[:5]
    media = ""
    if p.get("image"):
        media = f'<img src="{e(p["image"])}" alt="{e(p.get("alt") or title)}" loading="lazy" width="640" height="360">'
    proof = f'<p class="proof" data-k="p.{e(name)}.proof">{e(p["proof"])}</p>' if p.get("proof") else ""
    when = (r.get("pushed_at") or "")[:10]
    meta = [f'★ {r["stargazers_count"]} <span data-u="stars">{en["stars"]}</span>'] if r["stargazers_count"] else []
    meta += [e(r["language"])] if r.get("language") else []
    meta += [f'<span data-u="updated">{en["updated"]}</span> <time datetime="{when}">{when}</time>'] if when else []
    links = f'<a href="{e(url)}" data-u="code">{en["code"]}</a>'
    if live:
        links += f'<a href="{e(live)}" data-u="live">{en["live"]}</a>'
    kw = " ".join([name, r.get("language") or "", " ".join(tags), " ".join(r.get("topics") or [])])
    return f"""<article class="card fx" id="p-{e(name)}" data-s="{e(kw)}" data-kind="projects">{media}
<h3><a href="{e(url)}">{e(title)}</a></h3>
<p data-k="p.{e(name)}.pitch">{e(p.get("pitch") or r.get("description") or "")}</p>{proof}
<ul class="tags">{"".join(f"<li>{e(t)}</li>" for t in tags)}</ul>
<p class="meta">{" · ".join(meta)}</p><p class="links">{links}</p></article>"""


def jsonld(plan: dict, picked: list) -> str:
    links = [v for k, v in plan.get("links", {}).items() if v.startswith("https://")]
    person = {"@type": "Person", "@id": plan["url"] + "#person", "name": plan["name"], "url": plan["url"],
              "description": plan["tagline"], "sameAs": links, "knowsAbout": plan.get("skills", [])}
    if plan.get("job"):
        person["jobTitle"] = plan["job"]
    items = [{"@type": "ListItem", "position": i + 1, "item": {
        "@type": "SoftwareSourceCode", "name": p.get("title") or r["name"], "codeRepository": r["html_url"],
        "description": p.get("pitch") or r.get("description") or "", "programmingLanguage": r.get("language") or ""}}
        for i, (p, r) in enumerate(picked)]
    graph = [person, {"@type": "WebSite", "url": plan["url"], "name": plan["name"]},
             {"@type": "ProfilePage", "url": plan["url"], "mainEntity": {"@id": plan["url"] + "#person"},
              "dateModified": datetime.date.today().isoformat()},
             {"@type": "ItemList", "name": "Projects", "itemListElement": items}]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("<", "\\u003c")


def page(plan: dict, picked: list, ui: dict, names: dict) -> str:
    en = ui["en"]
    langs = [l for l in plan.get("langs", list(names)) if l in names] or ["en"]
    title = f'{plan["name"]} — {plan.get("job") or plan["headline"]}'
    desc = plan.get("description") or plan["tagline"]
    css = (HERE / "assets/site.css").read_text(encoding="utf-8")
    js = (HERE / "assets/site.js").read_text(encoding="utf-8")
    data = json.dumps({"ui": {l: ui[l] for l in langs}, "t": plan.get("t", {}), "names": names},
                      ensure_ascii=False).replace("<", "\\u003c")
    opts = "".join(f'<li role="option" id="l-{l}" data-l="{l}" lang="{l}" aria-selected="false">{e(names[l])}</li>' for l in langs)
    themes = "".join(f'<option value="{t}">{t.title()}</option>' for t in THEMES)
    sound = (f'<button id="sound" type="button" aria-pressed="false" data-u="sound">{en["sound"]}</button>'
             if plan.get("sound", True) else "")
    skills = plan.get("skills") or []
    xp = plan.get("experience") or []
    skills_html = (f'<section id="skills" class="wrap fx"><h2 data-u="skills">{en["skills"]}</h2><ul class="chips">'
                   + "".join(f'<li data-s="{e(s)}" data-kind="skills"><b>{e(s)}</b></li>' for s in skills)
                   + "</ul></section>") if skills else ""
    xp_html = (f'<section id="experience" class="wrap fx"><h2 data-u="experience">{en["experience"]}</h2><ul class="xp">'
               + "".join(f'<li data-s="{e(x.get("keywords", ""))}" data-kind="experience"><b>{e(x["role"])}</b>'
                         f'<span>{e(x.get("org", ""))} · {e(x.get("years", ""))}</span>'
                         f'<p data-k="xp.{i}">{e(x.get("text", ""))}</p></li>' for i, x in enumerate(xp))
               + "</ul></section>") if xp else ""
    contact = "".join(f'<a href="{e(v)}" rel="me">{e(k.title() if k != "x" else "X")}</a>'
                      for k, v in plan.get("links", {}).items())
    og = plan["url"] + "og.png"
    meta = f"""<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="author" content="{e(plan["name"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{e(plan["url"])}">
<meta property="og:type" content="profile"><meta property="og:url" content="{e(plan["url"])}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(og)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(title)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{e(og)}">
<script type="application/ld+json">{jsonld(plan, picked)}</script>"""
    cards = "\n".join(card(p, r, en) for p, r in picked)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
{meta}
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="sitemap" type="application/xml" href="sitemap.xml">
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main" data-u="skip">{en["skip"]}</a>
<header class="nav"><div class="wrap nav-in">
<a class="brand" href="#top">{e(plan["name"])}</a>
<nav aria-label="Sections"><a href="#projects" data-u="projects">{en["projects"]}</a><a href="#about" data-u="about">{en["about"]}</a><a href="#contact" data-u="contact">{en["contact"]}</a></nav>
<div class="opts">
<div class="langs"><button id="lang-btn" type="button" aria-haspopup="listbox" aria-expanded="false" aria-controls="lang-list" data-ua="aria-label:lang" aria-label="{en["lang"]}">🌐 <span>English</span></button>
<ul id="lang-list" role="listbox" tabindex="-1" hidden data-ua="aria-label:lang" aria-label="{en["lang"]}">{opts}</ul></div>
<select id="theme" data-ua="aria-label:theme" aria-label="{en["theme"]}">{themes}</select>
{sound}
</div></div></header>
<main id="main">
<section class="hero wrap" id="top">
<h1 data-k="headline">{e(plan["headline"])}</h1>
<p data-k="tagline">{e(plan["tagline"])}</p>
<div class="search" role="search"><input id="q" type="search" role="combobox" autocomplete="off" aria-autocomplete="list" aria-expanded="false" aria-controls="qr" data-ua="placeholder:search" placeholder="{en["search"]}" aria-label="{en["search"]}"><ul id="qr" role="listbox" hidden></ul></div>
<p class="cta"><a href="#projects" data-u="projects">{en["projects"]}</a><a href="#contact" data-u="contact">{en["contact"]}</a></p>
</section>
<section id="projects" class="wrap"><h2 data-u="projects">{en["projects"]}</h2><div class="grid">
{cards}
</div></section>
{skills_html}
{xp_html}
<section id="about" class="wrap fx"><h2 data-u="about">{en["about"]}</h2><p data-k="about">{e(plan.get("about", ""))}</p></section>
<section id="contact" class="wrap fx"><h2 data-u="contact">{en["contact"]}</h2><p class="contact">{contact}</p></section>
</main>
<footer><div class="wrap"><span data-u="foot">{en["foot"]}</span> · © {datetime.date.today().year} {e(plan["name"])}</div></footer>
<script id="i18n" type="application/json">{data}</script>
<script>{js}</script>
</body>
</html>
"""


def og_png(plan: dict, picked: list, out: pathlib.Path) -> bool:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("warn: Pillow not installed, og.png skipped (pip install pillow)", file=sys.stderr)
        return False
    fonts = [os.environ.get("FONT", ""), "/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"]
    path = next((f for f in fonts if f and os.path.exists(f)), None)
    f = (lambda s: ImageFont.truetype(path, s)) if path else (lambda s: ImageFont.load_default(s))
    im = Image.new("RGB", (1200, 630), (16, 16, 20))
    dr = ImageDraw.Draw(im)
    acc, fg, mut = (90, 169, 255), (245, 245, 247), (167, 167, 176)
    dr.rectangle([0, 0, 1200, 8], fill=acc)
    initials = "".join(w[0] for w in plan["name"].split()[:2]).upper()
    dr.rounded_rectangle([80, 70, 150, 140], 18, fill=acc)
    dr.text((115, 105), initials, font=f(30), fill=(16, 16, 20), anchor="mm")
    dr.text((172, 86), plan["name"], font=f(34), fill=fg)
    wrapped, line = [], ""
    for w in plan["headline"].split():
        if len(line + " " + w) > 30:
            wrapped.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    wrapped.append(line)
    dr.multiline_text((80, 190), "\n".join(wrapped[:3]), font=f(64), fill=fg, spacing=10)
    top = " · ".join((p.get("title") or r["name"]) for p, r in picked[:3])
    dr.text((80, 470), top[:70], font=f(26), fill=mut)
    dr.line([80, 525, 1120, 525], fill=(50, 50, 56), width=2)
    dr.text((80, 548), plan["url"].replace("https://", "").rstrip("/"), font=f(26), fill=acc)
    im.save(out / "og.png", optimize=True)
    return True


def side_files(plan: dict, picked: list, out: pathlib.Path) -> None:
    url, today = plan["url"], datetime.date.today().isoformat()
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {url}sitemap.xml\n", encoding="utf-8")
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"<url><loc>{e(url)}</loc><lastmod>{today}</lastmod></url>\n</urlset>\n", encoding="utf-8")
    lines = [f"# {plan['name']}", "", f"> {plan['tagline']}", "", plan.get("about", ""), "", "## Projects", ""]
    lines += [f"- [{p.get('title') or r['name']}]({r['html_url']}): {p.get('pitch') or r.get('description') or ''}"
              + (f" {p['proof']}" if p.get("proof") else "") for p, r in picked]
    if plan.get("skills"):
        lines += ["", "## Skills", "", ", ".join(plan["skills"])]
    lines += ["", "## Contact", ""] + [f"- {k}: {v}" for k, v in plan.get("links", {}).items()]
    (out / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    initials = e("".join(w[0] for w in plan["name"].split()[:2]).upper())
    (out / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0a66d1"/>'
        f'<text x="32" y="42" font-family="system-ui,sans-serif" font-size="26" font-weight="700" fill="#fff" '
        f'text-anchor="middle">{initials}</text></svg>\n', encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repos")
    ap.add_argument("plan")
    ap.add_argument("--out", default="site")
    a = ap.parse_args()
    repos = {r["name"]: r for r in load(a.repos)["repos"]}
    plan = load(a.plan)
    plan["url"] = plan.get("url", "").rstrip("/") + "/"
    errs = validate(plan, repos)
    if errs:
        sys.exit("plan.json errors:\n  " + "\n  ".join(errs))
    picked = [(p, repos[p["repo"]]) for p in plan["projects"]]
    ui, names = ui_table()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page(plan, picked, ui, names), encoding="utf-8")
    side_files(plan, picked, out)
    og = og_png(plan, picked, out)
    print(f"built {out}/: index.html, {len(picked)} projects, {'og.png, ' if og else ''}robots.txt, sitemap.xml, llms.txt, favicon.svg")


if __name__ == "__main__":
    main()

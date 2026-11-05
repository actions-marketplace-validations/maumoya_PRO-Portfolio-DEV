---
name: pro-portfolio-dev
description: Plans, builds and publishes a developer portfolio landing page from the user's public GitHub repos, live on GitHub Pages with SEO, JSON-LD, llms.txt, sitemap, a 1200x630 share image, 8 themes, 10 languages, smart search over projects, skills and experience, and an optional calm sound. Uses only real repo facts. Use when the user says "/pro-portfolio-dev", "build my portfolio", "make a portfolio from my GitHub", "portfolio landing page", "turn my repos into a website", "developer portfolio site", "publish my portfolio on GitHub Pages", "update my portfolio with my new repos", or asks for a personal site that shows their projects.
license: MIT
---

# PRO Portfolio DEV

GitHub user in, live portfolio out. Scripts do the fetching, building, checking and publishing;
you do the one thing they cannot: choose the projects and write honest, punchy copy.
Paths are relative to this skill's folder. Work in a scratch folder, e.g. `portfolio/`.

## 1 · Fetch (facts only)

`python3 scripts/fetch.py USER --out portfolio/repos.json` (2 public API calls, no token).
It prints the top repos. These are the only facts you may use; never invent stars, users or results.

## 2 · Plan (ask, then write `portfolio/plan.json`)

Ask in one message, with defaults the user can accept by saying "go":
- **Who and for whom:** name, role, the audience (recruiters, clients, peers). Default: GitHub name and bio.
- **Projects:** propose the 4-9 strongest (stars, recent pushes, a homepage, a clear description); they pick.
- **Skills and experience** to make searchable (optional), and contact links.
- **Where it lives:** `USER.github.io` (root) or a repo's `docs/` folder. The URL must be final.

Then write `plan.json` (schema and copy rules: `references/plan.md`). Copy rules in short: headline ≤8 words,
tagline says what + for whom, each project gets a one-line pitch (the benefit, not the stack) and an optional
`proof` line that quotes a number found in that repo's README or GitHub data, never one you made up.

**Languages:** UI strings for 10 languages ship in `scripts/ui.json`. To translate the user's own copy, add
`plan.t.<lang>` and translate by meaning, the way a native writer would say it in that language, not word for
word (see `references/plan.md`, "Translating"). Then re-read each language once as a native reader and fix
anything that sounds literal.

## 3 · Build and check

```
python3 scripts/build.py portfolio/repos.json portfolio/plan.json --out portfolio/site
python3 scripts/check.py portfolio/site
```
`check.py` must print `PASS`. Open `portfolio/site/index.html` in a browser and look at it before publishing:
try the search with a typo, switch to Arabic (right to left) and a dark theme.

## 4 · Publish (outward: ask first)

Show the user the page and the target, and get a yes. Then:
`bash scripts/publish.sh portfolio/site REPO_CLONE URL [--folder root|docs] --yes`
It commits, pushes, turns Pages on if needed and polls until the new build is live, printing `LIVE … in N s`.

## 5 · Measure and report

Report in ≤4 lines: the live URL, `LIVE` time, the `check.py` score, and Lighthouse SEO / accessibility /
performance from PageSpeed Insights (pagespeed.web.dev, free) or a local `lighthouse` if installed.

## Done when

- `check.py` prints `PASS` on the built site.
- Every project on the page is a real repo of the user, and every number on it traces to GitHub data or a README.
- The live URL returns the new build (`publish.sh` printed `LIVE`), or the user chose not to publish.

## Never

- Invent projects, metrics, employers or testimonials. Ask instead.
- Push, publish or enable Pages without the user's yes.
- Add trackers, analytics, cookies or external scripts. The page makes no third-party requests.
- Overwrite an existing site without showing what changes (`publish.sh` without `--yes` is the dry run).

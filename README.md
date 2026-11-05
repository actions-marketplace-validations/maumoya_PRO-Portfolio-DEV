<p align="center">
  <img src="assets/header.png" alt="PRO-Portfolio-DEV, a free open source Claude Code skill that turns your GitHub repos into a live portfolio page: 23 of 23 checks passed, Lighthouse SEO and accessibility 100, live in 23 seconds" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-7c5cfc" alt="Claude Code skill and plugin">
  <a href="#results-measured-2026-11-04"><img src="https://img.shields.io/badge/Lighthouse%20SEO%20%C2%B7%20a11y-100%20%C2%B7%20100-2da44e" alt="Lighthouse SEO 100 and accessibility 100 on the live demo"></a>
  <a href="#results-measured-2026-11-04"><img src="https://img.shields.io/badge/repos%20to%20live%20page-23%20s-2da44e" alt="From repo list to live page in 23 seconds"></a>
  <a href="https://github.com/marketplace/actions/portfolio-page-seo-check"><img src="https://img.shields.io/badge/GitHub%20Marketplace-Portfolio%20page%20SEO%20check-2088FF?logo=github" alt="GitHub Marketplace: Portfolio page SEO check"></a>
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license">
  <a href="https://opensource.org/license/mit"><img src="https://img.shields.io/badge/Open%20Source-OSI%20approved%20license-3DA639?logo=opensourceinitiative&logoColor=white" alt="Open Source: OSI-approved MIT license"></a>
  <a href="PRIVACY.md"><img src="https://img.shields.io/badge/privacy-no%20tracking%20%C2%B7%20no%20data%20collected-7c5cfc" alt="Privacy: no tracking, no data collected"></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/maumoya/PRO-Portfolio-DEV"><img src="https://api.scorecard.dev/projects/github.com/maumoya/PRO-Portfolio-DEV/badge" alt="OpenSSF Scorecard"></a>
</p>

# PRO Portfolio DEV

**Your repos already prove what you can do. Put them on one page that recruiters find.**

A Claude Code skill that plans, builds and publishes your portfolio landing page from your public GitHub repos:

- **Real facts only.** Stars, languages and links come from GitHub; every proof line quotes a README. Nothing invented.
- **Found by search engines and AI.** SEO tags, JSON-LD, sitemap, llms.txt and a 1200x630 share image, checked by 23 tests before it ships.
- **Ready for any visitor.** 10 languages (Arabic right to left), 8 themes, typo-proof search, zero trackers, zero external requests.
- **Live in under a minute.** It asks before publishing, pushes to GitHub Pages and times the deploy until the page is live.

<p align="center"><a href="https://maumoya.github.io/PRO-Portfolio-DEV/"><img src="assets/demo.gif" alt="Demo, 9 seconds: typing the typo finanse finds Finance automation, then the page switches to Spanish, Japanese, right-to-left Arabic and the ocean theme" width="720"></a></p>
<p align="center"><b><a href="https://maumoya.github.io/PRO-Portfolio-DEV/">Open the live demo</a></b> · built by this skill from <a href="https://github.com/maumoya">@maumoya</a>'s repos</p>

## Install

Claude Code plugin:

```
/plugin marketplace add maumoya/PRO-Portfolio-DEV
/plugin install pro-portfolio-dev@pro-portfolio-dev
```

Any agent that reads skills:

```
npx skills add maumoya/PRO-Portfolio-DEV
```

## Use

Type `/pro-portfolio-dev` or say "build my portfolio from my GitHub".
It fetches your repos, proposes the strongest 4 to 9, writes the copy with you, builds and checks the page,
and publishes only after you say yes.

## Results (measured 2026-11-04)

The live demo, built from real repos of [@maumoya](https://github.com/maumoya) (8 projects, 10 languages).

| Metric | Result | How it was measured |
|---|---|---|
| Repo list to live page | **23 s** | `fetch.py` → `build.py` → `check.py` → `publish.sh`, wall clock until the new build answered on github.io (324 s on a run where GitHub had two Pages builds queued) |
| Local build (fetch + build + check) | **1 s** | same run, before the push |
| Page checks | **23 / 23** | `check.py`: share tags, JSON-LD, sitemap, 1200x630 image, alt text, page weight, translations |
| Lighthouse SEO / accessibility / best practices | **100 / 100 / 100** | Lighthouse, mobile, [report](launch/lighthouse/report.html) |
| Largest paint, layout shift (lab) | **167 ms, 0** | Chrome trace, mobile, slow 4G, 4x CPU slowdown; a lab figure, not field data |
| Script cost | **$0** | 2 public GitHub API calls, no token, no paid service |
| Third-party requests on the page | **0** | no trackers, fonts or CDNs |

One site and one owner: a direction, not a guarantee. Check your own page with the Action below.

## Check a portfolio page in CI (GitHub Action)

The same read-only `check.py` runs as an Action on any static site, built by this skill or not. It makes no
network calls, fails the job below your score and writes a summary.

```yaml
- uses: maumoya/PRO-Portfolio-DEV@v0.1.0
  with:
    site: site          # folder with index.html
    min-score: 100      # percent of checks that must pass
```

Outputs: `passed`, `total`, `score`. Listed on the
[GitHub Marketplace](https://github.com/marketplace/actions/portfolio-page-seo-check).

## What comes next

Picked from the numbers above:

1. **Field data, not lab data.** Lighthouse is 100 in the lab; next is real-visitor numbers from PageSpeed Insights once the demo has traffic.
2. **Steadier deploy.** 22 of the 23 s is GitHub Pages building; with two builds queued it took 324 s. A Pages Actions deploy could make it steadier.
3. **Reach.** Stars, clones and visits get measured weekly and published here, so you can see if it works for people other than me.

## How it is tested

- `tests/` runs 9 offline unit tests on every PR (build, refuse unknown repos, HTML escaping, all 10 languages, a broken share image fails).
- `fuzz/` runs 60 s of [Atheris](https://github.com/google/atheris) fuzzing on `check.py` on every PR; it found and fixed two crashes.
- `.github/workflows/action-test.yml` runs the Action on a good site (must score 100) and a broken one (must fail).
- `evals/` holds one case per promise. Run `claude plugin eval . --allow-tools` (real model runs, billed to your account).

## FAQ

### What does it do?

Turns your public GitHub repos into a live portfolio landing page on GitHub Pages, with SEO, JSON-LD, llms.txt,
sitemap, share image, 10 languages, 8 themes, search and an optional calm sound. Real repo facts only.

### Does it send my data anywhere?

No. It reads your public repos from the GitHub API and pushes only to your own repo, after you say yes.
The page has no analytics, cookies or external scripts.

### Can I use it without Claude?

Yes for checking: the GitHub Action runs `check.py` on any static site. Building needs an agent to write the copy.

## About the author

Hi, I'm **Mauricio Alonso Moya Tapia** ([@maumoya](https://github.com/maumoya)). I built PRO-Portfolio-DEV so a portfolio shows only what the repos can prove, and stays current with them.

I build agent skills for Claude, systems to drive profits, and fast browser games. Open source, signed and measured.

More of my work:

- [adhd-status](https://github.com/maumoya/adhd-status): say STATUS, get one tiny table and one next step. Eval score 0.96 vs 0.50 without the skill.
- [resource-optimizer](https://github.com/maumoya/resource-optimizer): frees disk space safely; freed 21% of a real Mac mini disk.
- [maumoya.github.io](https://maumoya.github.io): my portfolio of agent tools and browser games.

Say hi or follow my work on [my website](https://maumoya.github.io) · [GitHub](https://github.com/maumoya).

## License

MIT © 2026 Mauricio Alonso Moya Tapia

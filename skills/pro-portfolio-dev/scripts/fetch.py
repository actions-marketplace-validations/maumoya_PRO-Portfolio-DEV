#!/usr/bin/env python3
"""Read a GitHub user's public profile and repos into one JSON file (the facts the page may use).

  python3 fetch.py USER [--out repos.json] [--forks] [--archived]

Two unauthenticated GET requests to api.github.com (60/hour limit). Reads no token, writes only --out.
"""
import argparse
import json
import sys
import urllib.request

API = "https://api.github.com"
KEEP = ("name", "description", "html_url", "homepage", "language", "topics",
        "stargazers_count", "forks_count", "pushed_at", "created_at", "fork", "archived")


def get(path):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "pro-portfolio-dev"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("user")
    ap.add_argument("--out", default="repos.json")
    ap.add_argument("--forks", action="store_true", help="keep forks")
    ap.add_argument("--archived", action="store_true", help="keep archived repos")
    a = ap.parse_args()
    if not a.user.replace("-", "").isalnum():
        sys.exit("not a GitHub user name: " + a.user)
    u = get(f"/users/{a.user}")
    repos = get(f"/users/{a.user}/repos?per_page=100&sort=pushed&type=owner")
    keep = [{k: r.get(k) for k in KEEP} for r in repos
            if (a.forks or not r["fork"]) and (a.archived or not r["archived"])]
    keep.sort(key=lambda r: (r["stargazers_count"], r["pushed_at"] or ""), reverse=True)
    out = {"user": {k: u.get(k) for k in ("login", "name", "bio", "blog", "location",
                                          "twitter_username", "html_url", "avatar_url", "public_repos")},
           "repos": keep}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"wrote {a.out}: {len(keep)} of {len(repos)} repos (forks and archived {'kept' if a.forks else 'dropped'})")
    for r in keep[:15]:
        print(f"  {r['stargazers_count']:>4}★  {r['name']:<32} {(r['description'] or '')[:60]}")


if __name__ == "__main__":
    main()

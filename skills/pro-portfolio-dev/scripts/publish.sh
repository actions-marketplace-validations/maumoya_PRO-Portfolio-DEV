#!/usr/bin/env bash
# Publish a built site to GitHub Pages and time it until the live URL serves the new page.
# Usage: publish.sh SITE_DIR REPO_DIR URL [--folder docs|root] [--yes]
#   REPO_DIR: a local clone of the repo that serves Pages (USER.github.io -> root, any other repo -> docs).
#   Without --yes it only copies and shows the diff summary (dry run). With --yes it commits, pushes,
#   turns Pages on (main, that folder) when it is off, and polls URL until it returns the new build (max 10 min).
# Network writes happen only with --yes: git push and one `gh api` call. Needs git and gh.
set -euo pipefail
site="${1:?usage: publish.sh SITE_DIR REPO_DIR URL [--folder docs|root] [--yes]}"
repo="${2:?missing REPO_DIR}"; url="${3:?missing URL}"; shift 3
folder=docs; yes=0
while [ $# -gt 0 ]; do
  case "$1" in --folder) folder="$2"; shift 2 ;; --yes) yes=1; shift ;; *) echo "unknown: $1" >&2; exit 2 ;; esac
done
[ -f "$site/index.html" ] || { echo "no $site/index.html: run build.py first" >&2; exit 1; }
[ -d "$repo/.git" ] || { echo "$repo is not a git clone" >&2; exit 1; }
start=$(date +%s)
dest="$repo"; [ "$folder" = root ] || dest="$repo/$folder"
mkdir -p "$dest"
stamp="ppd-$(date +%Y%m%d%H%M%S)"
cp -R "$site/." "$dest/"
# A build stamp the poller can look for, so a cached old page never counts as live.
python3 - "$dest/index.html" "$stamp" <<'PY'
import sys
p, s = sys.argv[1], sys.argv[2]
t = open(p, encoding="utf-8").read().replace("<head>", f'<head>\n<meta name="build" content="{s}">', 1)
open(p, "w", encoding="utf-8").write(t)
PY
git -C "$repo" add -A "${folder/root/.}"
git -C "$repo" status --short | head -20
if [ "$yes" != 1 ]; then echo "dry run: re-run with --yes to commit, push and enable Pages"; exit 0; fi

git -C "$repo" commit -q -m "feat: publish portfolio ($stamp)"
git -C "$repo" push -q
slug=$(git -C "$repo" remote get-url origin | sed -E 's#(git@github.com:|https://github.com/)##; s#\.git$##')
path="/"; [ "$folder" = root ] || path="/$folder"
if ! gh api "repos/$slug/pages" >/dev/null 2>&1; then
  gh api -X POST "repos/$slug/pages" -f "source[branch]=main" -f "source[path]=$path" >/dev/null
  echo "Pages turned on: main $path"
fi
for _ in $(seq 1 120); do
  if curl -fsSL "$url?$stamp" 2>/dev/null | grep -q "$stamp"; then
    echo "LIVE $url in $(( $(date +%s) - start )) s (build $stamp)"; exit 0
  fi
  sleep 5
done
echo "not live after 10 min: check https://github.com/$slug/actions" >&2; exit 1

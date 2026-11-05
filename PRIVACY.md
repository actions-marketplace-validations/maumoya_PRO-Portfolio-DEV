# Privacy

PRO-Portfolio-DEV is instructions and local scripts. It has no tracking and collects no data.

- `fetch.py` reads your **public** repos from the GitHub API (2 calls, no token) and saves them only to the folder you choose.
- `publish.sh` pushes only to your own repo, and only after you say yes.
- The page it builds has no analytics, cookies, external scripts, fonts or CDNs. Language, theme and sound choices are kept in the visitor's own browser (`localStorage`) and never leave it.
- The GitHub Action (`action.yml`) reads the site folder in your workflow and makes no network calls.

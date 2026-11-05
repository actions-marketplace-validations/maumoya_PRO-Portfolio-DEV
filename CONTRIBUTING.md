# Contributing

Thanks for helping. PRO-Portfolio-DEV is one skill file, one reference file and five small scripts (fetch, build, check, publish, UI strings).

## How to contribute

- **Bugs and ideas:** open an [issue](https://github.com/maumoya/PRO-Portfolio-DEV/issues). Say what you asked,
  what the skill or script did, and what you expected. A link to the built page helps.
- **Security problems:** do not open a public issue; follow [SECURITY.md](SECURITY.md).
- **Translations:** fixes to `skills/pro-portfolio-dev/scripts/ui.json` are welcome from native speakers.
- **Changes:** fork, branch, and open a pull request against `main`.

## Requirements for a pull request

- English only in code and docs, plain words, short sentences.
- Keep the skill's promise: real repo facts only, nothing published without the user's yes.
- The page makes no third-party requests: no trackers, analytics, cookies, fonts or CDNs (see [PRIVACY.md](PRIVACY.md)).
- The Lint, Action self-test and CodeQL checks must pass before merge.

## Tests

Offline unit tests (build, check, escaping, translations), also run in CI:

```bash
python3 -m pip install --require-hashes -r tests/requirements.txt
python3 -m unittest discover -s tests -v
bash scripts/lint_skill.sh
```

Model-graded cases in `evals/`, in the format `claude plugin eval` reads (real model runs, billed to your account):

```bash
claude plugin eval . --allow-tools
```

**Policy:** every change to the skill's or scripts' behavior adds or updates a test in `tests/` or a case in
`evals/` that would fail without the change. Pull requests that change behavior without a test are not merged.

## License

By contributing you agree that your contribution is licensed under the [MIT License](LICENSE).

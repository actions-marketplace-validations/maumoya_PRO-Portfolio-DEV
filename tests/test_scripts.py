"""Offline tests: build a site from the fixture, check it, and prove bad plans and unsafe text are refused."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = ROOT / "skills" / "pro-portfolio-dev" / "scripts"
FIX = pathlib.Path(__file__).resolve().parent / "fixture"
sys.path.insert(0, str(S))
import build  # noqa: E402
import check  # noqa: E402


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True)


class BuildAndCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.out = pathlib.Path(self.tmp.name) / "site"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def build(self, plan: dict) -> subprocess.CompletedProcess:
        p = pathlib.Path(self.tmp.name) / "plan.json"
        p.write_text(json.dumps(plan), encoding="utf-8")
        return run(str(S / "build.py"), str(FIX / "repos.json"), str(p), "--out", str(self.out))

    def plan(self) -> dict:
        return json.loads((FIX / "plan.json").read_text(encoding="utf-8"))

    def test_fixture_builds_and_passes_check(self) -> None:
        self.assertEqual(self.build(self.plan()).returncode, 0)
        res = check.run(self.out)
        self.assertTrue(all(ok for _, ok in res), [n for n, ok in res if not ok])

    def test_unknown_repo_is_refused(self) -> None:
        plan = self.plan()
        plan["projects"][0]["repo"] = "made-up-repo"
        r = self.build(plan)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("made-up-repo", r.stderr)

    def test_missing_required_and_http_url_refused(self) -> None:
        plan = self.plan()
        del plan["headline"]
        plan["url"] = "http://example.com/"
        errs = build.validate(plan, json.loads((FIX / "repos.json").read_text(encoding="utf-8")))
        self.assertTrue(any("headline" in e for e in errs))
        self.assertTrue(any("url" in e for e in errs))

    def test_html_in_plan_is_escaped(self) -> None:
        plan = self.plan()
        plan["headline"] = "<script>alert(1)</script>"
        plan["projects"][0]["pitch"] = '"><img src=x onerror=alert(1)>'
        self.assertEqual(self.build(plan).returncode, 0)
        html = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)", html)
        self.assertNotIn("<img src=x", html)

    def test_translation_and_rtl_data_present(self) -> None:
        self.build(self.plan())
        html = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn("Herramientas que lo demuestran.", html)
        for code in ("ar", "ja", "it"):
            self.assertIn(f'"{code}"', html)

    def test_check_fails_on_broken_site(self) -> None:
        self.build(self.plan())
        (self.out / "og.png").write_bytes(b"not a png")
        names = [n for n, ok in check.run(self.out) if not ok]
        self.assertIn("og.png 1200x630", names)


class UiStrings(unittest.TestCase):
    def test_every_language_has_every_key(self) -> None:
        ui = json.loads((S / "ui.json").read_text(encoding="utf-8"))
        keys = ui["_keys"]
        for lang, vals in ui.items():
            if not lang.startswith("_"):
                self.assertEqual(len(vals), len(keys), lang)
        self.assertEqual(len([k for k in ui if not k.startswith("_")]), 10)


if __name__ == "__main__":
    unittest.main()

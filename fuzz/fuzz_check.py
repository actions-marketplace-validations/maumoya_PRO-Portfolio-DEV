"""Atheris fuzz target: check.py's HTML scan and i18n check must never crash on any input.

Run: python3 -m pip install --require-hashes -r fuzz/requirements.txt
     python3 fuzz/fuzz_check.py -max_total_time=60
"""
import pathlib
import sys

import atheris

with atheris.instrument_imports():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills/pro-portfolio-dev/scripts"))
    import check


def TestOneInput(data: bytes) -> None:
    text = atheris.FuzzedDataProvider(data).ConsumeUnicodeNoSurrogates(len(data))
    scan = check.Scan()
    scan.feed(text)
    scan.close()
    check.i18n_check(text)
    check.i18n_check(scan.i18n)


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

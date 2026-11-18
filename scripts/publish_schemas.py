#!/usr/bin/env python3
"""Publish the AgentsML JSON Schemas to the GitHub Pages site.

Copies every ``schemas/**/*.json`` file to ``docs/schemas/`` with the same
relative layout, so the ``$id`` of each schema resolves to a real URL under
``https://indoos.github.io/agentsml/schemas/``. Each schema's ``$id`` must equal
its published URL; the script fails otherwise.

Usage:
    python3 scripts/publish_schemas.py          # copy schemas into docs/schemas/
    python3 scripts/publish_schemas.py --check  # exit 1 if docs/schemas/ is out of date
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "schemas"
DST = ROOT / "docs" / "schemas"
BASE_URL = "https://indoos.github.io/agentsml/schemas/"


def source_files() -> list[Path]:
    return sorted(p.relative_to(SRC) for p in SRC.rglob("*.json"))


def id_errors(rels: list[Path]) -> list[str]:
    errors = []
    for rel in rels:
        data = json.loads((SRC / rel).read_text(encoding="utf-8"))
        want = BASE_URL + rel.as_posix()
        if data.get("$id") != want:
            errors.append(f"{rel}: $id is {data.get('$id')!r}, expected {want!r}")
    return errors


def check(rels: list[Path]) -> int:
    problems = []
    for rel in rels:
        dst = DST / rel
        if not dst.is_file():
            problems.append(f"missing: docs/schemas/{rel}")
        elif dst.read_bytes() != (SRC / rel).read_bytes():
            problems.append(f"differs: docs/schemas/{rel}")
    if DST.is_dir():
        for p in sorted(DST.rglob("*.json")):
            rel = p.relative_to(DST)
            if rel not in rels:
                problems.append(f"stale: docs/schemas/{rel}")
    if problems:
        for line in problems:
            print(line, file=sys.stderr)
        print("published schemas are out of date; run: python3 scripts/publish_schemas.py",
              file=sys.stderr)
        return 1
    print(f"published schemas are up to date ({len(rels)} files)")
    return 0


def publish(rels: list[Path]) -> int:
    DST.mkdir(parents=True, exist_ok=True)
    for rel in rels:
        dst = DST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = (SRC / rel).read_bytes()
        if not dst.is_file() or dst.read_bytes() != data:
            dst.write_bytes(data)
            print(f"copied schemas/{rel} -> docs/schemas/{rel}")
    for p in sorted(DST.rglob("*.json")):
        rel = p.relative_to(DST)
        if rel not in rels:
            p.unlink()
            print(f"removed stale docs/schemas/{rel}")
    print(f"published {len(rels)} schema files")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="do not write; exit 1 if docs/schemas/ is out of date")
    args = ap.parse_args()

    rels = source_files()
    if not rels:
        print(f"error: no schemas found under {SRC}", file=sys.stderr)
        return 2
    errors = id_errors(rels)
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    return check(rels) if args.check else publish(rels)


if __name__ == "__main__":
    sys.exit(main())

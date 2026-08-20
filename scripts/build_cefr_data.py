from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


CEFR_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}
WORD_RE = re.compile(r"^[a-z]+(?:['-][a-z]+)*$")


def _variants(headword: str) -> list[str]:
    variants = []
    for value in headword.split("/"):
        normalized = value.strip().lower().replace("’", "'")
        if WORD_RE.fullmatch(normalized):
            variants.append(normalized)
    return variants


def _read_levels(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            level = (row.get("CEFR") or "").strip().upper()
            if level not in CEFR_LEVELS:
                continue
            for word in _variants(row.get("headword") or ""):
                rows.append((word, level))
    return rows


def build_cefr_mapping(
    cefr_j_path: Path,
    c1_c2_path: Path,
    output: Path,
) -> tuple[int, int]:
    """Build a word-only mapping and omit every ambiguous CEFR headword."""
    levels_by_word: dict[str, set[str]] = defaultdict(set)
    for path in (cefr_j_path, c1_c2_path):
        if not path.is_file():
            raise FileNotFoundError(f"CEFR source does not exist: {path}")
        for word, level in _read_levels(path):
            levels_by_word[word].add(level)

    known = {
        word: next(iter(levels))
        for word, levels in levels_by_word.items()
        if len(levels) == 1
    }
    ambiguous = sorted(
        word for word, levels in levels_by_word.items() if len(levels) > 1
    )
    payload = {
        "meta": {
            "description": (
                "Unambiguous word-level CEFR labels compiled from CEFR-J 1.5 "
                "and Octanove C1/C2 1.0. Ambiguous headwords are omitted."
            ),
            "known_words": len(known),
            "ambiguous_words_omitted": len(ambiguous),
            "sources": [
                "CEFR-J Vocabulary Profile 1.5",
                "Octanove Vocabulary Profile C1/C2 1.0",
            ],
        },
        "levels": dict(sorted(known.items())),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f"{output.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)
    return len(known), len(ambiguous)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build StudyForge's reliable partial CEFR mapping."
    )
    parser.add_argument("cefr_j", type=Path, help="CEFR-J vocabulary CSV path.")
    parser.add_argument("c1_c2", type=Path, help="Octanove C1/C2 CSV path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("studyforge/data/cefr_levels.json"),
    )
    args = parser.parse_args()
    known, ambiguous = build_cefr_mapping(args.cefr_j, args.c1_c2, args.output)
    print(
        f"Created {args.output} with {known:,} reliable entries; "
        f"omitted {ambiguous:,} ambiguous headwords."
    )


if __name__ == "__main__":
    main()

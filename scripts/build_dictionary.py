from __future__ import annotations

import argparse
import csv
import re
import sqlite3
from pathlib import Path


WORD_RE = re.compile(r"^[a-z][a-z'-]{1,39}$")
EXCHANGE_FORM_RE = re.compile(r"^(?:p|d|i|3|r|t|s):(.+)$")


def parse_int(value: str | None) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def normalize_pos(pos: str | None, translation: str) -> str:
    value = (pos or "").strip()
    if value:
        return value
    matches = re.findall(
        r"(?:^|\\n|\n)(n|v|vt|vi|a|ad|adj|r|adv|prep|conj|pron|num|art|int|aux)\.",
        translation.lower(),
    )
    return "/".join(dict.fromkeys(matches))


def is_useful(row: dict[str, str]) -> bool:
    word = (row.get("word") or "").strip().lower()
    translation = (row.get("translation") or "").strip()
    if not WORD_RE.fullmatch(word) or not translation:
        return False
    if any(char.isdigit() for char in word):
        return False
    frq = parse_int(row.get("frq"))
    bnc = parse_int(row.get("bnc"))
    tag = (row.get("tag") or "").lower()
    oxford = bool((row.get("oxford") or "").strip())
    exam_word = any(
        value in tag
        for value in ("gk", "zk", "cet4", "cet6", "ky", "toefl", "ielts", "gre")
    )
    return oxford or exam_word or (0 < frq <= 45000) or (0 < bnc <= 35000)


def build_database(source: Path, output: Path) -> tuple[int, int]:
    if not source.is_file():
        raise FileNotFoundError(f"Dictionary source does not exist: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_name(f"{output.name}.tmp")
    temporary_output.unlink(missing_ok=True)

    entry_rows: list[tuple] = []
    exchange_by_word: dict[str, str] = {}
    with source.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not is_useful(row):
                continue
            word = (row.get("word") or "").strip().lower()
            translation = (row.get("translation") or "").strip()
            entry_rows.append(
                (
                    word,
                    (row.get("phonetic") or "").strip(),
                    translation,
                    normalize_pos(row.get("pos"), translation),
                    parse_int(row.get("frq")),
                    parse_int(row.get("bnc")),
                    1 if (row.get("oxford") or "").strip() else 0,
                    (row.get("tag") or "").strip(),
                )
            )
            exchange_by_word[word] = (row.get("exchange") or "").strip()

    form_rows: dict[str, str] = {}
    for lemma, exchange in exchange_by_word.items():
        for segment in exchange.split("/"):
            match = EXCHANGE_FORM_RE.match(segment.strip().lower())
            if not match:
                continue
            for form in match.group(1).split(","):
                form = form.strip()
                if WORD_RE.fullmatch(form) and form != lemma:
                    form_rows.setdefault(form, lemma)

    connection = sqlite3.connect(temporary_output)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = DELETE")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.executescript(
            """
            CREATE TABLE entries (
                word TEXT PRIMARY KEY,
                phonetic TEXT NOT NULL DEFAULT '',
                translation TEXT NOT NULL,
                pos TEXT NOT NULL DEFAULT '',
                frq_rank INTEGER NOT NULL DEFAULT 0,
                bnc_rank INTEGER NOT NULL DEFAULT 0,
                oxford INTEGER NOT NULL DEFAULT 0,
                tags TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE forms (
                form TEXT PRIMARY KEY,
                lemma TEXT NOT NULL REFERENCES entries(word)
            );
            CREATE INDEX idx_forms_lemma ON forms(lemma);
            """
        )
        connection.executemany(
            """
            INSERT OR REPLACE INTO entries
            (word, phonetic, translation, pos, frq_rank, bnc_rank, oxford, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            entry_rows,
        )
        connection.executemany(
            "INSERT OR IGNORE INTO forms (form, lemma) VALUES (?, ?)",
            form_rows.items(),
        )
        connection.commit()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise sqlite3.DatabaseError(f"Dictionary integrity check failed: {integrity}")
        connection.execute("PRAGMA optimize")
    except Exception:
        connection.close()
        temporary_output.unlink(missing_ok=True)
        raise
    else:
        connection.close()
        temporary_output.replace(output)
    return len(entry_rows), len(form_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build StudyForge's local dictionary.")
    parser.add_argument("source", type=Path, help="Path to ECDICT's stardict.csv")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("studyforge/data/studyforge_dictionary.db"),
        help="Output SQLite database path",
    )
    args = parser.parse_args()
    entries, forms = build_database(args.source, args.output)
    print(f"Created {args.output} with {entries:,} entries and {forms:,} forms.")


if __name__ == "__main__":
    main()

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from studyforge.fallback_dictionary import FALLBACK_ENTRIES, FALLBACK_FORMS
from studyforge.models import DictionaryEntry


class DictionaryStore:
    """Read-only access to the generated ECDICT subset, with an offline fallback."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.using_fallback = not self.database_path.is_file()
        self._entry_count: int | None = None

    def _connect(self) -> sqlite3.Connection:
        database_uri = self.database_path.resolve().as_posix()
        connection = sqlite3.connect(
            f"file:{database_uri}?mode=ro&immutable=1",
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        return connection

    @property
    def entry_count(self) -> int:
        if self.using_fallback:
            return len(FALLBACK_ENTRIES)
        if self._entry_count is None:
            try:
                with self._connect() as connection:
                    self._entry_count = int(
                        connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
                    )
            except sqlite3.Error:
                self.using_fallback = True
                self._entry_count = len(FALLBACK_ENTRIES)
        return self._entry_count

    def resolve_many(
        self, words: Iterable[str]
    ) -> tuple[dict[str, str], dict[str, DictionaryEntry]]:
        normalized_words = sorted({word.lower() for word in words if word})
        if not normalized_words:
            return {}, {}
        if self.using_fallback:
            return self._fallback_resolve(normalized_words)

        try:
            return self._database_resolve(normalized_words)
        except (sqlite3.Error, OSError):
            self.using_fallback = True
            return self._fallback_resolve(normalized_words)

    def _database_resolve(
        self, words: list[str]
    ) -> tuple[dict[str, str], dict[str, DictionaryEntry]]:
        resolved: dict[str, str] = {}
        entries: dict[str, DictionaryEntry] = {}
        with self._connect() as connection:
            for chunk_start in range(0, len(words), 800):
                chunk = words[chunk_start : chunk_start + 800]
                placeholders = ",".join("?" for _ in chunk)

                # Prefer a known inflection mapping over a standalone dictionary
                # entry so cards use "analyze", not "analyzed".
                form_rows = connection.execute(
                    f"""
                    SELECT f.form, e.word, e.phonetic, e.translation, e.pos,
                           e.frq_rank, e.bnc_rank, e.oxford, e.tags
                    FROM forms AS f
                    JOIN entries AS e ON e.word = f.lemma
                    WHERE f.form IN ({placeholders})
                    """,
                    chunk,
                ).fetchall()
                for row in form_rows:
                    entry = _row_to_entry(row)
                    entries[entry.word] = entry
                    resolved[str(row["form"])] = entry.word

                unresolved = [word for word in chunk if word not in resolved]
                if not unresolved:
                    continue
                direct_placeholders = ",".join("?" for _ in unresolved)
                direct_rows = connection.execute(
                    f"""
                    SELECT word, phonetic, translation, pos, frq_rank, bnc_rank, oxford, tags
                    FROM entries WHERE word IN ({direct_placeholders})
                    """,
                    unresolved,
                ).fetchall()
                for row in direct_rows:
                    entry = _row_to_entry(row)
                    entries[entry.word] = entry
                    resolved[entry.word] = entry.word
        return resolved, entries

    def _fallback_resolve(
        self, words: list[str]
    ) -> tuple[dict[str, str], dict[str, DictionaryEntry]]:
        resolved: dict[str, str] = {}
        entries: dict[str, DictionaryEntry] = {}
        for form in words:
            lemma = form if form in FALLBACK_ENTRIES else FALLBACK_FORMS.get(form)
            if not lemma:
                continue
            phonetic, pos, translation = FALLBACK_ENTRIES[lemma]
            resolved[form] = lemma
            entries[lemma] = DictionaryEntry(
                word=lemma,
                phonetic=phonetic,
                translation=translation,
                part_of_speech=pos,
                frequency_rank=5000,
                bnc_rank=5000,
                oxford=True,
                tags="fallback",
            )
        return resolved, entries


def _row_to_entry(row: sqlite3.Row) -> DictionaryEntry:
    return DictionaryEntry(
        word=str(row["word"]),
        phonetic=str(row["phonetic"] or ""),
        translation=str(row["translation"] or ""),
        part_of_speech=str(row["pos"] or ""),
        frequency_rank=int(row["frq_rank"] or 0),
        bnc_rank=int(row["bnc_rank"] or 0),
        oxford=bool(row["oxford"]),
        tags=str(row["tags"] or ""),
    )

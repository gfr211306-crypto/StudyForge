from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PdfDocument:
    """Text extracted from a PDF."""

    pages: tuple[str, ...]

    @property
    def full_text(self) -> str:
        return "\n\n".join(page for page in self.pages if page)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def english_word_count(self) -> int:
        return len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)?", self.full_text))


@dataclass(frozen=True)
class DictionaryEntry:
    word: str
    phonetic: str
    translation: str
    part_of_speech: str
    frequency_rank: int = 0
    bnc_rank: int = 0
    oxford: bool = False
    tags: str = ""


@dataclass(frozen=True)
class VocabularyItem:
    word: str
    phonetic: str
    part_of_speech: str
    translation: str
    example: str
    count: int
    pages: tuple[int, ...]
    score: float
    cefr_level: str = "unknown"
    is_ielts: bool = False

    @property
    def page_label(self) -> str:
        if not self.pages:
            return "—"
        shown = ", ".join(str(page) for page in self.pages[:4])
        return f"{shown}…" if len(self.pages) > 4 else shown


@dataclass(frozen=True)
class AnalysisResult:
    """A reusable result returned by the public StudyForge API."""

    document: PdfDocument
    items: tuple[VocabularyItem, ...]
    mode: str

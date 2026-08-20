from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from studyforge.resources import default_cefr_path


CEFR_LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
CEFR_UNKNOWN = "unknown"
_VALID_WORD = re.compile(r"^[a-z]+(?:['-][a-z]+)*$")


def normalize_cefr_word(word: str) -> str:
    return word.replace("’", "'").strip().lower()


class CEFRProfile:
    """Reliable word-level CEFR lookups with explicit unknown fallbacks."""

    def __init__(self, levels: Mapping[str, str] | None = None):
        normalized: dict[str, str] = {}
        for word, level in (levels or {}).items():
            normalized_word = normalize_cefr_word(word)
            normalized_level = str(level).upper()
            if _VALID_WORD.fullmatch(normalized_word) and normalized_level in CEFR_LEVELS:
                normalized[normalized_word] = normalized_level
        self._levels = normalized

    @classmethod
    def from_json(cls, path: str | Path) -> "CEFRProfile":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        levels = data.get("levels", data)
        if not isinstance(levels, dict):
            raise ValueError("CEFR data must contain a 'levels' object.")
        return cls(levels)

    @classmethod
    def from_mapping(cls, levels: Mapping[str, str]) -> "CEFRProfile":
        return cls(levels)

    def level_for(self, word: str) -> str:
        """Return A1-C2 only for a known unambiguous entry; otherwise unknown."""
        return self._levels.get(normalize_cefr_word(word), CEFR_UNKNOWN)

    def classify_many(self, words: list[str] | tuple[str, ...]) -> dict[str, str]:
        return {word: self.level_for(word) for word in words}

    @property
    def known_word_count(self) -> int:
        return len(self._levels)


@lru_cache(maxsize=1)
def default_cefr_profile() -> CEFRProfile:
    path = default_cefr_path()
    if not path.is_file():
        return CEFRProfile()
    return CEFRProfile.from_json(path)

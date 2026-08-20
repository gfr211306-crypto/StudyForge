from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any

from studyforge.cefr import CEFRProfile, default_cefr_profile
from studyforge.dictionary import DictionaryStore
from studyforge.models import AnalysisResult
from studyforge.pdf_reader import MAX_PDF_BYTES, PdfReadError, extract_pdf_text
from studyforge.resources import default_dictionary_path
from studyforge.vocabulary import LEVEL_LABELS, analyze_vocabulary


VALID_MODES = tuple(LEVEL_LABELS)


class StudyForge:
    """Reusable PDF vocabulary extraction service used by Web, CLI, and Python."""

    def __init__(
        self,
        dictionary_path: str | PathLike[str] | None = None,
        cefr_profile: CEFRProfile | None = None,
    ):
        self.dictionary = DictionaryStore(
            Path(dictionary_path) if dictionary_path else default_dictionary_path()
        )
        self.cefr_profile = cefr_profile or default_cefr_profile()

    def analyze_bytes(
        self,
        file_bytes: bytes,
        *,
        limit: int = 30,
        mode: str = "balanced",
        min_occurrences: int = 1,
    ) -> AnalysisResult:
        _validate_options(limit, mode, min_occurrences)
        document = extract_pdf_text(file_bytes)
        items = analyze_vocabulary(
            document,
            self.dictionary,
            limit=limit,
            level=mode,
            min_occurrences=min_occurrences,
            cefr_profile=self.cefr_profile,
        )
        return AnalysisResult(document=document, items=tuple(items), mode=mode)

    def analyze_file(
        self,
        path: str | PathLike[str],
        *,
        limit: int = 30,
        mode: str = "balanced",
        min_occurrences: int = 1,
    ) -> AnalysisResult:
        pdf_path = Path(path).expanduser()
        if not pdf_path.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if pdf_path.stat().st_size > MAX_PDF_BYTES:
            raise PdfReadError(
                f"PDF exceeds the {MAX_PDF_BYTES // (1024 * 1024)} MB limit."
            )
        return self.analyze_bytes(
            pdf_path.read_bytes(),
            limit=limit,
            mode=mode,
            min_occurrences=min_occurrences,
        )


def analyze_pdf(
    path: str | PathLike[str],
    *,
    limit: int = 30,
    mode: str = "balanced",
    min_occurrences: int = 1,
    dictionary_path: str | PathLike[str] | None = None,
    cefr_profile: CEFRProfile | None = None,
) -> AnalysisResult:
    """Analyze a PDF file with the bundled core library."""
    return StudyForge(dictionary_path, cefr_profile).analyze_file(
        path,
        limit=limit,
        mode=mode,
        min_occurrences=min_occurrences,
    )


def analyze_pdf_bytes(
    file_bytes: bytes,
    *,
    limit: int = 30,
    mode: str = "balanced",
    min_occurrences: int = 1,
    dictionary_path: str | PathLike[str] | None = None,
    cefr_profile: CEFRProfile | None = None,
) -> AnalysisResult:
    """Analyze in-memory PDF bytes with the bundled core library."""
    return StudyForge(dictionary_path, cefr_profile).analyze_bytes(
        file_bytes,
        limit=limit,
        mode=mode,
        min_occurrences=min_occurrences,
    )


def _validate_options(limit: int, mode: str, min_occurrences: int) -> None:
    if not isinstance(limit, int) or not 1 <= limit <= 500:
        raise ValueError("limit must be an integer between 1 and 500.")
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of: {', '.join(VALID_MODES)}.")
    if not isinstance(min_occurrences, int) or not 1 <= min_occurrences <= 100:
        raise ValueError("min_occurrences must be an integer between 1 and 100.")

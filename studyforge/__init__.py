"""Reusable StudyForge PDF vocabulary extraction library."""

__version__ = "0.2.0"

from studyforge.api import StudyForge, analyze_pdf, analyze_pdf_bytes
from studyforge.cefr import CEFR_LEVELS, CEFR_UNKNOWN, CEFRProfile
from studyforge.exporter import export_rows, export_vocabulary
from studyforge.models import AnalysisResult, PdfDocument, VocabularyItem

__all__ = [
    "AnalysisResult",
    "CEFR_LEVELS",
    "CEFR_UNKNOWN",
    "CEFRProfile",
    "PdfDocument",
    "StudyForge",
    "VocabularyItem",
    "__version__",
    "analyze_pdf",
    "analyze_pdf_bytes",
    "export_rows",
    "export_vocabulary",
]

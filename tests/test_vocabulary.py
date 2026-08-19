from studyforge.dictionary import DictionaryStore
from studyforge.models import PdfDocument
from studyforge.vocabulary import analyze_vocabulary


def test_vocabulary_uses_pdf_sentence_and_counts_occurrences(tmp_path):
    document = PdfDocument(
        pages=(
            "Researchers analyze evidence to evaluate a complex theory. "
            "Strong evidence can significantly impact the final approach.",
            "The research process requires a consistent method. "
            "This method helps researchers analyze each important factor.",
        )
    )
    store = DictionaryStore(tmp_path / "missing.db")

    items = analyze_vocabulary(document, store, limit=20)
    by_word = {item.word: item for item in items}

    assert "analyze" in by_word
    assert by_word["analyze"].count == 2
    assert "Researchers analyze evidence" in by_word["analyze"].example
    assert by_word["analyze"].translation == "分析"


def test_vocabulary_respects_minimum_occurrences(tmp_path):
    document = PdfDocument(
        pages=("A specific strategy can benefit research and improve the process.",)
    )
    store = DictionaryStore(tmp_path / "missing.db")
    items = analyze_vocabulary(document, store, limit=20, min_occurrences=2)
    assert items == []

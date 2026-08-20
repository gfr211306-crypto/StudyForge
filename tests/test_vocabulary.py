import sqlite3

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
    assert by_word["analyze"].cefr_level == "B1"


def test_vocabulary_respects_minimum_occurrences(tmp_path):
    document = PdfDocument(
        pages=("A specific strategy can benefit research and improve the process.",)
    )
    store = DictionaryStore(tmp_path / "missing.db")
    items = analyze_vocabulary(document, store, limit=20, min_occurrences=2)
    assert items == []


def test_ielts_mode_prioritizes_explicit_ielts_dictionary_tags(tmp_path):
    database = tmp_path / "dictionary.db"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE entries (
            word TEXT PRIMARY KEY,
            phonetic TEXT,
            translation TEXT,
            pos TEXT,
            frq_rank INTEGER,
            bnc_rank INTEGER,
            oxford INTEGER,
            tags TEXT
        );
        CREATE TABLE forms (form TEXT PRIMARY KEY, lemma TEXT);
        INSERT INTO entries VALUES
          ('strategy', '', 'n. 策略', 'n', 3000, 3000, 1, ''),
          ('alleviate', '', 'v. 減輕', 'v', 12000, 12000, 0, 'ielts');
        """
    )
    connection.commit()
    connection.close()

    document = PdfDocument(
        pages=(
            "A strategy can improve results. This strategy supports learning. "
            "Another strategy may alleviate pressure.",
        )
    )
    items = analyze_vocabulary(
        document,
        DictionaryStore(database),
        limit=10,
        level="ielts",
    )
    assert items[0].word == "alleviate"
    assert items[0].is_ielts is True
    assert items[0].cefr_level == "C1"

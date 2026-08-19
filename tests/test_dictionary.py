import sqlite3

from studyforge.dictionary import DictionaryStore


def test_dictionary_resolves_direct_words_and_inflections(tmp_path):
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
          ('analyze', 'ana-laiz', 'v. 分析', 'v', 5000, 6000, 1, 'cet6'),
          ('analyzed', '', 'v. 已分析', 'v', 7000, 8000, 0, '');
        INSERT INTO forms VALUES ('analyzed', 'analyze');
        """
    )
    connection.commit()
    connection.close()

    store = DictionaryStore(database)
    resolved, entries = store.resolve_many(["analyze", "analyzed", "unknown"])

    assert resolved["analyze"] == "analyze"
    assert resolved["analyzed"] == "analyze"
    assert entries["analyze"].translation == "v. 分析"

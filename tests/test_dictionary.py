import sqlite3

from studyforge.dictionary import DictionaryStore


class TrackingConnection(sqlite3.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.close_called = False

    def close(self):
        self.close_called = True
        super().close()


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


def test_dictionary_closes_connections_after_queries(tmp_path, monkeypatch):
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
          ('analyze', 'ana-laiz', 'v. 分析', 'v', 5000, 6000, 1, 'cet6');
        INSERT INTO forms VALUES ('analyzed', 'analyze');
        """
    )
    connection.commit()
    connection.close()

    connections = []

    def connect():
        tracked = sqlite3.connect(database, factory=TrackingConnection)
        tracked.row_factory = sqlite3.Row
        connections.append(tracked)
        return tracked

    store = DictionaryStore(database)
    monkeypatch.setattr(store, "_connect", connect)

    assert store.entry_count == 1
    resolved, entries = store.resolve_many(["analyzed"])
    assert resolved == {"analyzed": "analyze"}
    assert entries["analyze"].translation == "v. 分析"

    close_calls = [tracked.close_called for tracked in connections]
    for tracked in connections:
        if not tracked.close_called:
            tracked.close()

    assert close_calls == [True, True]

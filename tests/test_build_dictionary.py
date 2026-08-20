import csv
import sqlite3

from scripts.build_dictionary import build_database
from studyforge.dictionary import DictionaryStore


def test_build_dictionary_creates_valid_database_and_inflections(tmp_path):
    source = tmp_path / "ecdict.csv"
    output = tmp_path / "dictionary.db"
    with source.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "word",
                "phonetic",
                "translation",
                "pos",
                "frq",
                "bnc",
                "oxford",
                "tag",
                "exchange",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "word": "analyze",
                "phonetic": "ana-laiz",
                "translation": "v. 分析",
                "pos": "v:100",
                "frq": "5000",
                "bnc": "6000",
                "oxford": "1",
                "tag": "cet6",
                "exchange": "p:analyzed/i:analyzing/3:analyzes",
            }
        )

    entries, forms = build_database(source, output)
    assert entries == 1
    assert forms == 3

    connection = sqlite3.connect(output)
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    connection.close()

    resolved, dictionary_entries = DictionaryStore(output).resolve_many(["analyzed"])
    assert resolved["analyzed"] == "analyze"
    assert dictionary_entries["analyze"].translation == "v. 分析"

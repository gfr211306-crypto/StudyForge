import csv
import io
import json

from studyforge.exporter import build_anki_csv, build_csv, build_json


def test_anki_csv_has_bom_headers_and_html_fields():
    data = build_anki_csv(
        [
            {
                "英文單字": "analyze",
                "音標": "ˈænəlaɪz",
                "詞性": "動詞",
                "中文意思": "分析",
                "PDF 例句": "We analyze the evidence.",
                "頁碼": "1, 2",
                "CEFR": "B1",
                "IELTS": True,
            }
        ]
    )

    assert data.startswith(b"\xef\xbb\xbf")
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
    assert rows[0] == ["Front", "Back", "Tags"]
    assert "analyze" in rows[1][0]
    assert "<b>動詞</b>" in rows[1][1]
    assert "CEFR B1" in rows[1][1]
    assert "StudyForge" in rows[1][2]
    assert "IELTS" in rows[1][2]


def test_anki_csv_wraps_formula_like_user_input_in_html():
    data = build_anki_csv(
        [
            {
                "英文單字": "=1+1",
                "中文意思": "@SUM(A1:A2)",
            }
        ]
    )
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
    assert rows[1][0].startswith("<span>")
    assert rows[1][1].startswith("<span>")
    assert not rows[1][0].startswith("=")
    assert not rows[1][1].startswith("@")


def test_plain_csv_has_stable_fields_and_formula_protection():
    data = build_csv(
        [
            {
                "word": "=danger",
                "translation": "分析",
                "count": 2,
                "pages": [1, 3],
                "cefr": "B2",
                "is_ielts": True,
            }
        ]
    )
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    assert rows[0]["word"] == "'=danger"
    assert rows[0]["pages"] == "1;3"
    assert rows[0]["cefr"] == "B2"
    assert rows[0]["is_ielts"] == "true"


def test_json_export_preserves_types_and_unicode():
    data = build_json(
        [
            {
                "word": "analyze",
                "translation": "分析",
                "count": 2,
                "pages": [1, 3],
                "cefr": "B1",
                "is_ielts": False,
            }
        ]
    )
    records = json.loads(data)
    assert records[0]["translation"] == "分析"
    assert records[0]["count"] == 2
    assert records[0]["pages"] == [1, 3]
    assert records[0]["is_ielts"] is False


def test_exporters_normalize_invalid_optional_numbers():
    records = json.loads(
        build_json(
            [
                {
                    "word": "analyze",
                    "count": "not-a-number",
                    "pages": ["1", "bad", 2],
                }
            ]
        )
    )
    assert records[0]["count"] == 0
    assert records[0]["pages"] == [1, 2]

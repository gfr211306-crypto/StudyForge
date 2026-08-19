import csv
import io

from studyforge.exporter import build_anki_csv


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
            }
        ]
    )

    assert data.startswith(b"\xef\xbb\xbf")
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
    assert rows[0] == ["Front", "Back", "Tags"]
    assert "analyze" in rows[1][0]
    assert "<b>動詞</b>" in rows[1][1]
    assert "StudyForge" in rows[1][2]

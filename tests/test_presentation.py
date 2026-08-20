from studyforge.presentation import build_word_card_html


def test_word_card_preview_escapes_user_and_pdf_content():
    result = build_word_card_html(
        {
            "英文單字": "<script>alert(1)</script>",
            "音標": "<img src=x>",
            "詞性": "<b>verb</b>",
            "中文意思": "分析 & 評估",
            "PDF 例句": "<svg onload=alert(1)>",
            "CEFR": "<b>B1</b>",
            "IELTS": True,
        }
    )

    assert "<script>" not in result
    assert "<svg" not in result
    assert "&lt;script&gt;" in result
    assert "&lt;svg onload=alert(1)&gt;" in result
    assert "分析 &amp; 評估" in result
    assert "CEFR &lt;b&gt;B1&lt;/b&gt; · IELTS" in result

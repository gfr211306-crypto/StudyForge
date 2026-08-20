import pymupdf

from studyforge import AnalysisResult, StudyForge, analyze_pdf, analyze_pdf_bytes


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_textbox(pymupdf.Rect(72, 72, 520, 760), text, fontsize=11)
    data = document.tobytes()
    document.close()
    return data


def test_public_api_analyzes_bytes_and_files(tmp_path):
    data = make_pdf(
        "Students analyze evidence and evaluate a significant research strategy. "
        "This strategy can improve learning outcomes."
    )
    path = tmp_path / "lesson.pdf"
    path.write_bytes(data)

    byte_result = analyze_pdf_bytes(data, limit=10)
    file_result = analyze_pdf(path, limit=10)
    service_result = StudyForge().analyze_file(path, limit=10)

    for result in (byte_result, file_result, service_result):
        assert isinstance(result, AnalysisResult)
        assert result.document.page_count == 1
        assert result.items
        assert all(item.cefr_level for item in result.items)


def test_public_api_validates_modes_and_limits():
    service = StudyForge()
    data = make_pdf("Research evidence supports effective learning strategies.")
    for kwargs in (
        {"limit": 0},
        {"mode": "made-up"},
        {"min_occurrences": 0},
    ):
        try:
            service.analyze_bytes(data, **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected ValueError for {kwargs}")

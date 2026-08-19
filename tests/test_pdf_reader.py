import pymupdf
import pytest

from studyforge.pdf_reader import PdfReadError, extract_pdf_text


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text, fontsize=11)
    data = document.tobytes()
    document.close()
    return data


def test_extract_pdf_text_reads_page_content():
    document = extract_pdf_text(
        make_pdf("Research evidence indicates significant benefits for students.")
    )
    assert document.page_count == 1
    assert "Research evidence" in document.full_text
    assert document.english_word_count == 7


def test_extract_pdf_text_rejects_empty_input():
    with pytest.raises(PdfReadError, match="空"):
        extract_pdf_text(b"")

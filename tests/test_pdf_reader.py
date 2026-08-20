import pymupdf
import pytest

import studyforge.pdf_reader as pdf_reader
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


def test_extract_pdf_text_rejects_oversized_file(monkeypatch):
    monkeypatch.setattr(pdf_reader, "MAX_PDF_BYTES", 10)
    with pytest.raises(PdfReadError, match="MB 上限"):
        extract_pdf_text(b"x" * 11)


def test_extract_pdf_text_rejects_too_many_pages(monkeypatch):
    document = pymupdf.open()
    for _ in range(3):
        page = document.new_page()
        page.insert_text((72, 72), "Enough English words for PDF validation.")
    data = document.tobytes()
    document.close()

    monkeypatch.setattr(pdf_reader, "MAX_PDF_PAGES", 2)
    with pytest.raises(PdfReadError, match="2 頁上限"):
        extract_pdf_text(data)


def test_extract_pdf_text_rejects_excessive_extracted_text(monkeypatch):
    monkeypatch.setattr(pdf_reader, "MAX_EXTRACTED_CHARACTERS", 20)
    with pytest.raises(PdfReadError, match="文字內容過多"):
        extract_pdf_text(
            make_pdf("Research evidence indicates significant benefits for students.")
        )

from __future__ import annotations

import re

import pymupdf

from studyforge.models import PdfDocument


class PdfReadError(ValueError):
    """Raised when a PDF cannot provide usable text."""


def _clean_page_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(file_bytes: bytes) -> PdfDocument:
    """Extract sorted plain text from every page of an in-memory PDF."""
    if not file_bytes:
        raise PdfReadError("這份檔案是空的，請重新選擇 PDF。")

    try:
        pdf = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PdfReadError("無法開啟這份 PDF；檔案可能已損壞或不是有效的 PDF。") from exc

    try:
        if pdf.needs_pass:
            raise PdfReadError("這份 PDF 有密碼保護，請先解除密碼後再上傳。")
        if pdf.page_count == 0:
            raise PdfReadError("這份 PDF 沒有任何頁面。")

        pages = tuple(_clean_page_text(page.get_text("text", sort=True)) for page in pdf)
        full_text = "\n".join(pages)

        if len(full_text.strip()) < 20:
            raise PdfReadError(
                "幾乎讀不到文字。這可能是掃描圖片型 PDF，請先進行 OCR，"
                "讓文字可以被反白選取後再試一次。"
            )

        english_words = re.findall(r"[A-Za-z]{2,}", full_text)
        if len(english_words) < 5:
            raise PdfReadError("這份 PDF 中的英文內容太少，無法整理英文單字。")

        metadata = {
            str(key): str(value or "")
            for key, value in (pdf.metadata or {}).items()
            if value
        }
        return PdfDocument(pages=pages, metadata=metadata)
    finally:
        pdf.close()

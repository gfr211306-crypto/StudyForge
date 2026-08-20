from __future__ import annotations

import re

import pymupdf

from studyforge.models import PdfDocument


MAX_PDF_BYTES = 25 * 1024 * 1024
MAX_PDF_PAGES = 400
MAX_EXTRACTED_CHARACTERS = 2_000_000


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
    if len(file_bytes) > MAX_PDF_BYTES:
        raise PdfReadError(
            f"PDF 超過 {MAX_PDF_BYTES // (1024 * 1024)} MB 上限，"
            "請壓縮或分割檔案後再試一次。"
        )

    try:
        pdf = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise PdfReadError("無法開啟這份 PDF；檔案可能已損壞或不是有效的 PDF。") from exc

    try:
        if pdf.needs_pass:
            raise PdfReadError("這份 PDF 有密碼保護，請先解除密碼後再上傳。")
        if pdf.page_count == 0:
            raise PdfReadError("這份 PDF 沒有任何頁面。")
        if pdf.page_count > MAX_PDF_PAGES:
            raise PdfReadError(
                f"PDF 超過 {MAX_PDF_PAGES} 頁上限，請分割檔案後再試一次。"
            )

        pages_list: list[str] = []
        character_count = 0
        for page in pdf:
            page_text = _clean_page_text(page.get_text("text", sort=True))
            character_count += len(page_text)
            if character_count > MAX_EXTRACTED_CHARACTERS:
                raise PdfReadError("PDF 文字內容過多，請分割成較小的檔案後再試一次。")
            pages_list.append(page_text)

        pages = tuple(pages_list)
        full_text = "\n".join(pages)

        if len(full_text.strip()) < 20:
            raise PdfReadError(
                "幾乎讀不到文字。這可能是掃描圖片型 PDF，請先進行 OCR，"
                "讓文字可以被反白選取後再試一次。"
            )

        english_words = re.findall(r"[A-Za-z]{2,}", full_text)
        if len(english_words) < 5:
            raise PdfReadError("這份 PDF 中的英文內容太少，無法整理英文單字。")

        return PdfDocument(pages=pages)
    finally:
        pdf.close()

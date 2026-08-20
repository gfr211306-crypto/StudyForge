from __future__ import annotations

import csv
import html
import io
import json
import re
from collections.abc import Iterable, Mapping
from typing import Any, Literal

from studyforge.models import VocabularyItem


ExportFormat = Literal["anki", "csv", "json"]
EXPORT_FORMATS: tuple[ExportFormat, ...] = ("anki", "csv", "json")
EXPORT_MIME_TYPES = {
    "anki": "text/csv",
    "csv": "text/csv",
    "json": "application/json",
}


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _safe_text(value).lower() in {"1", "true", "yes", "y", "✓", "ielts"}


def _safe_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _tagify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_\-]+", "_", value.strip())
    return value.strip("_") or "pdf"


def _spreadsheet_safe(value: Any) -> str:
    text = _safe_text(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _normalize_row(row: Mapping[str, Any]) -> dict[str, Any]:
    pages_value = row.get("pages", row.get("頁碼", ""))
    if isinstance(pages_value, (list, tuple)):
        pages = [
            parsed
            for page in pages_value
            if (parsed := _safe_int(page)) > 0
        ]
        page_label = ", ".join(str(page) for page in pages)
    else:
        page_label = _safe_text(pages_value)
        pages = [
            int(value)
            for value in re.findall(r"\d+", page_label.replace("…", ""))
        ]

    cefr = _safe_text(row.get("cefr", row.get("CEFR", "unknown"))).upper()
    if cefr not in {"A1", "A2", "B1", "B2", "C1", "C2"}:
        cefr = "unknown"

    return {
        "word": _safe_text(row.get("word", row.get("英文單字"))),
        "phonetic": _safe_text(row.get("phonetic", row.get("音標"))),
        "part_of_speech": _safe_text(
            row.get("part_of_speech", row.get("詞性"))
        ),
        "translation": _safe_text(row.get("translation", row.get("中文意思"))),
        "example": _safe_text(row.get("example", row.get("PDF 例句"))),
        "count": _safe_int(row.get("count", row.get("出現次數", 0))),
        "pages": pages,
        "page_label": page_label,
        "cefr": cefr,
        "is_ielts": _safe_bool(row.get("is_ielts", row.get("IELTS", False))),
    }


def vocabulary_records(items: Iterable[VocabularyItem]) -> list[dict[str, Any]]:
    """Convert vocabulary items to stable, English-keyed public records."""
    return [
        {
            "word": item.word,
            "phonetic": item.phonetic,
            "part_of_speech": item.part_of_speech,
            "translation": item.translation,
            "example": item.example,
            "count": item.count,
            "pages": list(item.pages),
            "page_label": item.page_label,
            "cefr": item.cefr_level,
            "is_ielts": item.is_ielts,
        }
        for item in items
    ]


def export_vocabulary(
    items: Iterable[VocabularyItem], export_format: ExportFormat = "anki"
) -> bytes:
    """Export vocabulary items as Anki CSV, ordinary CSV, or JSON."""
    return export_rows(vocabulary_records(items), export_format)


def export_rows(
    rows: Iterable[Mapping[str, Any]], export_format: ExportFormat = "anki"
) -> bytes:
    """Export normalized mappings while preserving all CSV/HTML protections."""
    if export_format not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {export_format}")
    normalized = [_normalize_row(row) for row in rows]
    if export_format == "anki":
        return _build_anki_csv(normalized)
    if export_format == "csv":
        return _build_plain_csv(normalized)
    return _build_json(normalized)


def build_anki_csv(rows: Iterable[Mapping[str, Any]]) -> bytes:
    """Backward-compatible Anki exporter for editable Streamlit rows."""
    return export_rows(rows, "anki")


def build_csv(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return export_rows(rows, "csv")


def build_json(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return export_rows(rows, "json")


def output_suffix(export_format: str) -> str:
    if export_format not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {export_format}")
    return ".json" if export_format == "json" else ".csv"


def _build_anki_csv(rows: list[dict[str, Any]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Front", "Back", "Tags"])

    for row in rows:
        word = row["word"]
        if not word:
            continue
        front_content = html.escape(word)
        if row["phonetic"]:
            front_content += (
                f"<br><small>/{html.escape(row['phonetic'].strip('/'))}/</small>"
            )
        front = f"<span>{front_content}</span>"

        back_parts = []
        if row["part_of_speech"]:
            back_parts.append(f"<b>{html.escape(row['part_of_speech'])}</b>")
        if row["translation"]:
            back_parts.append(html.escape(row["translation"]))
        if row["example"]:
            back_parts.append(
                "<br><br><i>"
                + html.escape(row["example"]).replace("\n", "<br>")
                + "</i>"
            )
        badges = [f"CEFR {html.escape(row['cefr'])}"]
        if row["is_ielts"]:
            badges.append("IELTS")
        back_parts.append(f"<br><small>{' · '.join(badges)}</small>")
        if row["page_label"] and row["page_label"] != "—":
            back_parts.append(
                f"<br><small>PDF 第 {html.escape(row['page_label'])} 頁</small>"
            )
        back_content = "　".join(back_parts[:2]) + "".join(back_parts[2:])
        back = f"<span>{back_content}</span>"

        tags = [
            "StudyForge",
            "PDF_vocab",
            f"cefr_{_tagify(row['cefr'])}",
            _tagify(word),
        ]
        if row["is_ielts"]:
            tags.append("IELTS")
        writer.writerow([front, back, " ".join(tags)])

    return output.getvalue().encode("utf-8-sig")


def _build_plain_csv(rows: list[dict[str, Any]]) -> bytes:
    output = io.StringIO(newline="")
    fieldnames = [
        "word",
        "phonetic",
        "part_of_speech",
        "translation",
        "example",
        "count",
        "pages",
        "cefr",
        "is_ielts",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "word": _spreadsheet_safe(row["word"]),
                "phonetic": _spreadsheet_safe(row["phonetic"]),
                "part_of_speech": _spreadsheet_safe(row["part_of_speech"]),
                "translation": _spreadsheet_safe(row["translation"]),
                "example": _spreadsheet_safe(row["example"]),
                "count": row["count"],
                "pages": ";".join(str(page) for page in row["pages"]),
                "cefr": row["cefr"],
                "is_ielts": str(row["is_ielts"]).lower(),
            }
        )
    return output.getvalue().encode("utf-8-sig")


def _build_json(rows: list[dict[str, Any]]) -> bytes:
    records = [
        {
            key: value
            for key, value in row.items()
            if key != "page_label"
        }
        for row in rows
        if row["word"]
    ]
    return (
        json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")

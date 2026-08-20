from __future__ import annotations

import html
from typing import Any, Mapping


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else html.escape(text)


def build_word_card_html(row: Mapping[str, Any]) -> str:
    """Render an escaped HTML preview card for a user-editable vocabulary row."""
    word = _safe_text(row.get("英文單字"))
    phonetic = _safe_text(row.get("音標"))
    part_of_speech = _safe_text(row.get("詞性"))
    translation = _safe_text(row.get("中文意思"))
    example = _safe_text(row.get("PDF 例句")).replace("\n", "<br>")
    phonetic_html = f" /{phonetic.strip('/')}/" if phonetic else ""

    return (
        '<div class="word-card">'
        f"<strong>{word}</strong>{phonetic_html}"
        f'<div class="word-meta">{part_of_speech} · {translation}</div>'
        f'<div class="word-example">{example}</div>'
        "</div>"
    )

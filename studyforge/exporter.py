from __future__ import annotations

import csv
import html
import io
import re
from typing import Any, Iterable


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def _tagify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_\-]+", "_", value.strip())
    return value.strip("_") or "pdf"


def build_anki_csv(rows: Iterable[dict[str, Any]]) -> bytes:
    """Create an UTF-8-BOM CSV with Anki-friendly Front, Back and Tags fields."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Front", "Back", "Tags"])

    for row in rows:
        word = _safe_text(row.get("英文單字"))
        if not word:
            continue
        phonetic = _safe_text(row.get("音標"))
        pos = _safe_text(row.get("詞性"))
        translation = _safe_text(row.get("中文意思"))
        example = _safe_text(row.get("PDF 例句"))
        pages = _safe_text(row.get("頁碼"))

        front = html.escape(word)
        if phonetic:
            front += f"<br><small>/{html.escape(phonetic.strip('/'))}/</small>"

        back_parts = []
        if pos:
            back_parts.append(f"<b>{html.escape(pos)}</b>")
        if translation:
            back_parts.append(html.escape(translation))
        if example:
            back_parts.append(
                "<br><br><i>" + html.escape(example).replace("\n", "<br>") + "</i>"
            )
        if pages and pages != "—":
            back_parts.append(f"<br><small>PDF 第 {html.escape(pages)} 頁</small>")
        back = "　".join(back_parts[:2]) + "".join(back_parts[2:])
        tags = f"StudyForge PDF_vocab {_tagify(word)}"
        writer.writerow([front, back, tags])

    return output.getvalue().encode("utf-8-sig")

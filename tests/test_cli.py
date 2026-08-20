import json

import pymupdf

from studyforge.cli import main


def make_pdf(path):
    document = pymupdf.open()
    page = document.new_page()
    page.insert_textbox(
        pymupdf.Rect(72, 72, 520, 760),
        (
            "Students analyze evidence and evaluate a significant research strategy. "
            "This strategy can improve learning outcomes and alleviate pressure."
        ),
        fontsize=11,
    )
    document.save(path)
    document.close()


def test_cli_extracts_json_file(tmp_path, capsys):
    pdf = tmp_path / "lesson.pdf"
    output = tmp_path / "cards.json"
    make_pdf(pdf)

    exit_code = main(
        [
            "extract",
            str(pdf),
            "--limit",
            "8",
            "--mode",
            "ielts",
            "--format",
            "json",
            "--output",
            str(output),
        ]
    )
    captured = capsys.readouterr()
    records = json.loads(output.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert "Created" in captured.out
    assert len(records) <= 8
    assert all("cefr" in record and "is_ielts" in record for record in records)


def test_cli_reports_missing_pdf(capsys):
    exit_code = main(["extract", "missing.pdf"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "PDF file not found" in captured.err

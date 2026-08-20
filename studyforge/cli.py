from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence

from studyforge import __version__
from studyforge.api import StudyForge, VALID_MODES
from studyforge.exporter import EXPORT_FORMATS, export_vocabulary, output_suffix
from studyforge.pdf_reader import PdfReadError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="studyforge",
        description="Extract study vocabulary from English PDF files.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser(
        "extract",
        help="Extract vocabulary from a PDF.",
    )
    extract.add_argument("pdf", type=Path, help="Input PDF path.")
    extract.add_argument("--limit", type=int, default=30, help="Maximum word count.")
    extract.add_argument(
        "--format",
        choices=EXPORT_FORMATS,
        default="anki",
        help="Output format (default: anki).",
    )
    extract.add_argument(
        "--mode",
        choices=VALID_MODES,
        default="balanced",
        help="Vocabulary ranking mode, including ielts.",
    )
    extract.add_argument(
        "--min-occurrences",
        type=int,
        default=1,
        help="Minimum occurrences in the PDF.",
    )
    extract.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output path. Use '-' to write to stdout.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "extract":
        parser.error("A command is required.")

    try:
        result = StudyForge().analyze_file(
            args.pdf,
            limit=args.limit,
            mode=args.mode,
            min_occurrences=args.min_occurrences,
        )
        data = export_vocabulary(result.items, args.format)
        output = args.output or _default_output_path(args.pdf, args.format)
        if output == "-":
            sys.stdout.buffer.write(data)
            return 0

        output_path = Path(output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)
        print(f"Created {output_path} with {len(result.items)} vocabulary items.")
        return 0
    except (FileNotFoundError, PdfReadError, ValueError, OSError) as exc:
        print(f"studyforge: error: {exc}", file=sys.stderr)
        return 2


def _default_output_path(pdf_path: Path, export_format: str) -> str:
    safe_stem = re.sub(r"[^\w.-]+", "_", pdf_path.stem, flags=re.UNICODE).strip("._")
    suffix = output_suffix(export_format)
    return f"{safe_stem or 'studyforge'}_{export_format}{suffix}"

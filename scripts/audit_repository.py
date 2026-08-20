from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_TRACKED_FILE_BYTES = 50 * 1024 * 1024
SKIPPED_DIRECTORIES = {
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}
FORBIDDEN_PARTS = {
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
}
FORBIDDEN_NAMES = {
    ".env",
    "secrets.toml",
}
FORBIDDEN_SUFFIXES = {
    ".key",
    ".p12",
    ".pem",
    ".pfx",
    ".pyc",
}
SECRET_PATTERNS = {
    "OpenAI-style API key": re.compile(r"\bs" + r"k-[A-Za-z0-9_-]{20,}\b"),
    "GitHub token": re.compile(r"\bgh" + r"[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "Private key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?" + r"PRIVATE KEY-----"
    ),
    "Credential assignment": re.compile(
        r"""(?ix)
        \b(api[_-]?key|client[_-]?secret|password|access[_-]?token)\b
        \s*[:=]\s*
        ["'][^"'\r\n]{8,}["']
        """
    ),
}


def tracked_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return [
            path
            for path in PROJECT_ROOT.rglob("*")
            if path.is_file()
            and not any(
                part in SKIPPED_DIRECTORIES or part.endswith(".egg-info")
                for part in path.parts
            )
        ]
    return [
        PROJECT_ROOT / item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    ]


def scan() -> list[str]:
    problems: list[str] = []
    for path in tracked_files():
        relative = path.relative_to(PROJECT_ROOT)
        lower_parts = {part.lower() for part in relative.parts}
        if lower_parts & FORBIDDEN_PARTS:
            problems.append(f"Forbidden tracked path: {relative}")
        if path.name.lower() in FORBIDDEN_NAMES:
            problems.append(f"Forbidden tracked file: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            problems.append(f"Forbidden tracked file type: {relative}")
        if not path.is_file():
            problems.append(f"Tracked file is missing: {relative}")
            continue
        if path.stat().st_size > MAX_TRACKED_FILE_BYTES:
            problems.append(f"Tracked file exceeds 50 MB: {relative}")
            continue

        data = path.read_bytes()
        if b"\0" in data[:8192]:
            continue
        text = data.decode("utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                problems.append(f"Possible {label} in {relative}")

    return problems


def main() -> int:
    problems = scan()
    if problems:
        print("Repository audit failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("Repository audit passed: no forbidden tracked files or obvious secrets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

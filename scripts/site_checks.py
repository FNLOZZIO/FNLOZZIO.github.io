#!/usr/bin/env python3
"""Validate the public static pages contract for FNLOZZIO.github.io."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SMOKE_PATHS = [
    Path("index.html"),
    Path("assets/site.css"),
    Path("legal/amazon-portability-privacy/index.html"),
]
FORBIDDEN_PATTERNS = [
    re.compile(r"/mnt/[A-Za-z0-9_.-]+/"),
    re.compile(r"\b[A-Z]:\\\\[A-Za-z0-9_. -]+", re.IGNORECASE),
    re.compile(r"\\\\[A-Za-z0-9_.-]+\\\\[A-Za-z0-9$_.-]+"),
    re.compile(r"\b10\.(?:\d{1,3}\.){2}\d{1,3}\b"),
    re.compile(r"\b192\.168\.(?:\d{1,3}\.)\d{1,3}\b"),
    re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3}\b"),
]


class CheckError(RuntimeError):
    """Raised when one or more checks fail."""


@dataclass
class HtmlReferenceCollector(HTMLParser):
    refs: list[str] = field(default_factory=list)
    title_seen: bool = False

    def __post_init__(self) -> None:
        super().__init__()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "title":
            self.title_seen = True
        for key in ("href", "src"):
            value = attr_map.get(key)
            if value:
                self.refs.append(value)


def _iter_html_files() -> list[Path]:
    return sorted(path for path in REPO_ROOT.rglob("*.html") if ".git" not in path.parts)


def _normalize_local_ref(ref: str, source_file: Path) -> Path | None:
    if not ref or ref.startswith("#"):
        return None
    parsed = urlparse(ref)
    if parsed.scheme or ref.startswith("//"):
        return None
    path_part = parsed.path
    if not path_part:
        return None
    if path_part.startswith("/"):
        candidate = REPO_ROOT / path_part.lstrip("/")
    else:
        candidate = source_file.parent / path_part
    if path_part.endswith("/"):
        return candidate / "index.html"
    if candidate.exists():
        return candidate
    if candidate.suffix:
        return candidate
    return candidate / "index.html"


def _check_smoke() -> list[str]:
    errors: list[str] = []
    for rel_path in EXPECTED_SMOKE_PATHS:
        if not (REPO_ROOT / rel_path).exists():
            errors.append(f"missing expected public path: {rel_path}")
    return errors


def _check_html_integrity() -> list[str]:
    errors: list[str] = []
    html_files = _iter_html_files()
    if not html_files:
        return ["no HTML files found under repo root"]
    for html_file in html_files:
        contents = html_file.read_text(encoding="utf-8")
        if "<!doctype html>" not in contents.lower():
            errors.append(f"{html_file.relative_to(REPO_ROOT)}: missing <!doctype html>")
        parser = HtmlReferenceCollector()
        parser.feed(contents)
        if "<title>" not in contents.lower():
            errors.append(f"{html_file.relative_to(REPO_ROOT)}: missing <title>")
        for ref in parser.refs:
            target = _normalize_local_ref(ref, html_file)
            if target is None:
                continue
            if not target.exists():
                errors.append(
                    f"{html_file.relative_to(REPO_ROOT)}: broken local reference '{ref}' -> {target.relative_to(REPO_ROOT)}"
                )
    return errors


def _check_public_only_content() -> list[str]:
    errors: list[str] = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if ".git" in path.parts or path.is_dir():
            continue
        if path.suffix.lower() not in {".html", ".css", ".md", ".yaml", ".yml", ".txt"}:
            continue
        contents = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            match = pattern.search(contents)
            if match:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)}: contains forbidden public-only pattern '{match.group(0)}'"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("test", "smoke", "consistency"), default="test")
    args = parser.parse_args(argv)

    errors: list[str] = []
    errors.extend(_check_smoke())
    if args.mode in {"test", "consistency"}:
        errors.extend(_check_html_integrity())
    if args.mode == "consistency":
        errors.extend(_check_public_only_content())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        raise CheckError(f"{len(errors)} public-pages checks failed")
    print(f"public-pages {args.mode}: ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

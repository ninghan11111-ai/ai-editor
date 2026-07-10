#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "outputs",
    "debug_bundles",
    ".server_cache",
    "models",
    "checkpoints",
}

SECRET_PATTERNS = [
    re.compile(r"\b(sk-[A-Za-z0-9_\-]{20,})\b"),
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\b(github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"(?i)\b(api_key|access_token|authorization|password|secret)\s*=\s*['\"]([^'\"\s*][^'\"]{8,})['\"]"),
    re.compile(r"\b(PEXELS_API_KEY|OPENSTORYLINE_[A-Z0-9_]*API_KEY|TTS_[A-Z0-9_]*API_KEY)\s*=\s*['\"]?([^'\"\s]{12,})"),
]

ALLOW_VALUES = {"", "***", "REPLACE_WITH_REAL_KEY", "REPLACE_API_KEY", "sk-REPLACE_WITH_REAL_KEY"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan project files for likely committed secrets.")
    parser.add_argument("paths", nargs="*", help="Paths to scan. Defaults to tracked files.")
    parser.add_argument("--all", action="store_true", help="Scan all non-skipped files under the repo.")
    args = parser.parse_args()

    files = _iter_files(args.paths, scan_all=args.all)
    findings = []
    for path in files:
        findings.extend(_scan_file(path))

    if findings:
        print("Potential secrets found:")
        for path, lineno, snippet in findings:
            print(f"{path}:{lineno}: {snippet}")
        return 1

    print("No likely secrets found.")
    return 0


def _iter_files(paths: list[str], *, scan_all: bool) -> list[Path]:
    explicit_paths = bool(paths)
    if paths:
        candidates = [Path(p) for p in paths]
    elif scan_all:
        try:
            out = subprocess.check_output(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                text=True,
            )
            candidates = [Path(line) for line in out.splitlines() if line.strip()]
        except Exception:
            candidates = [p for p in Path(".").rglob("*") if p.is_file()]
    else:
        try:
            out = subprocess.check_output(["git", "ls-files"], text=True)
            candidates = [Path(line) for line in out.splitlines() if line.strip()]
        except Exception:
            candidates = [p for p in Path(".").rglob("*") if p.is_file()]

    return [p for p in candidates if _should_scan(p, explicit=explicit_paths)]


def _should_scan(path: Path, *, explicit: bool) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if not explicit and path.name == "config.local.toml":
        return False
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".mp4", ".mp3", ".wav", ".zip", ".pth", ".safetensors", ".deb"}:
        return False
    return path.exists() and path.is_file()


def _scan_file(path: Path) -> list[tuple[str, int, str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    findings = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pattern in SECRET_PATTERNS:
            m = pattern.search(line)
            if not m:
                continue
            value = m.group(m.lastindex or 1)
            if value in ALLOW_VALUES or value.strip() in ALLOW_VALUES:
                continue
            if "example" in path.name.lower() and "REPLACE" in line:
                continue
            findings.append((str(path), lineno, _mask_line(line)))
            break
    return findings


def _mask_line(line: str) -> str:
    s = line.strip()
    if len(s) <= 24:
        return "***"
    return f"{s[:18]}...{s[-6:]}"


if __name__ == "__main__":
    raise SystemExit(main())

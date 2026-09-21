#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_editor.config import default_config_path, load_settings  # noqa: E402
from ai_editor.resilience.run_manifest import mask_secrets  # noqa: E402


DEFAULT_SKIP_DIRS = {".git", ".venv", "__pycache__", "media"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a masked AI Editor debug bundle.")
    parser.add_argument("--session", required=True, help="Session id under outputs/")
    parser.add_argument("--outputs-dir", default=None, help="Override outputs directory")
    parser.add_argument("--cache-dir", default=None, help="Optional .server_cache directory")
    parser.add_argument("--out", default="debug_bundles", help="Output directory for the zip file")
    parser.add_argument("--include-media", action="store_true", help="Include media files. Off by default.")
    args = parser.parse_args()

    cfg = load_settings(default_config_path())
    outputs_dir = Path(args.outputs_dir or cfg.project.outputs_dir)
    cache_dir = Path(args.cache_dir or cfg.local_mcp_server.server_cache_dir)
    session_dir = outputs_dir / args.session
    if not session_dir.exists():
        raise SystemExit(f"session directory not found: {session_dir}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"debug_bundle_{args.session}.zip"

    with tempfile.TemporaryDirectory(prefix="ai-editor_debug_") as tmp:
        staging = Path(tmp) / f"debug_bundle_{args.session}"
        staging.mkdir(parents=True)

        _copy_tree_masked(session_dir, staging / "outputs" / args.session, include_media=args.include_media)

        cache_session_dir = cache_dir / args.session
        if cache_session_dir.exists():
            _copy_tree_masked(cache_session_dir, staging / "server_cache" / args.session, include_media=args.include_media)

        config_summary = _masked_config_summary(cfg)
        (staging / "config_summary.json").write_text(
            json.dumps(config_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (staging / "README.txt").write_text(
            "AI Editor debug bundle. Secrets are masked. Media files are excluded unless --include-media was used.\n",
            encoding="utf-8",
        )

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in staging.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(staging))

    print(zip_path)
    return 0


def _copy_tree_masked(src: Path, dst: Path, *, include_media: bool) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in DEFAULT_SKIP_DIRS]
        rel_root = root_path.relative_to(src)
        out_root = dst / rel_root
        out_root.mkdir(parents=True, exist_ok=True)

        for name in files:
            src_file = root_path / name
            if not include_media and src_file.suffix.lower() not in {".json", ".md", ".txt", ".log"}:
                continue
            dst_file = out_root / name
            if src_file.suffix.lower() == ".json":
                try:
                    data = json.loads(src_file.read_text(encoding="utf-8"))
                    dst_file.write_text(
                        json.dumps(mask_secrets(data), ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    continue
                except Exception:
                    pass
            shutil.copy2(src_file, dst_file)


def _masked_config_summary(cfg: Any) -> dict[str, Any]:
    data = cfg.model_dump(mode="json") if hasattr(cfg, "model_dump") else {}
    return mask_secrets(data)


if __name__ == "__main__":
    raise SystemExit(main())


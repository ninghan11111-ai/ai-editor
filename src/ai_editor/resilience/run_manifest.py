from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import tempfile


SENSITIVE_KEYS = {
    "api_key",
    "access_token",
    "authorization",
    "token",
    "password",
    "secret",
    "x-api-key",
    "apikey",
}


def _is_sensitive_key(key: Any) -> bool:
    normalized = str(key).lower().replace("-", "_")
    return any(token in normalized for token in SENSITIVE_KEYS)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def mask_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if _is_sensitive_key(k):
                out[k] = "***"
            else:
                out[k] = mask_secrets(v)
        return out
    if isinstance(value, list):
        return [mask_secrets(v) for v in value]
    if isinstance(value, tuple):
        return [mask_secrets(v) for v in value]
    if isinstance(value, str) and _looks_like_secret(value):
        return _mask_secret_string(value)
    return value


def append_node_event(
    *,
    outputs_dir: str | Path,
    session_id: str,
    event: dict[str, Any],
) -> Path:
    session_dir = Path(outputs_dir) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = session_dir / "run_manifest.json"

    if manifest_path.exists() and manifest_path.stat().st_size > 0:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    else:
        manifest = {}

    now = utc_now_iso()
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("session_id", session_id)
    manifest.setdefault("created_at", now)
    manifest["updated_at"] = now
    manifest.setdefault("nodes", [])
    manifest.setdefault("latest_by_node", {})

    safe_event = mask_secrets(dict(event))
    safe_event.setdefault("recorded_at", now)
    manifest["nodes"].append(safe_event)

    node_id = safe_event.get("node_id")
    if node_id:
        manifest["latest_by_node"][node_id] = safe_event

    if safe_event.get("fallback") or safe_event.get("status") == "fallback":
        manifest["degraded"] = True
        user_message = safe_event.get("user_message")
        if user_message:
            manifest.setdefault("warnings", [])
            manifest["warnings"].append(
                {
                    "node_id": node_id,
                    "artifact_id": safe_event.get("artifact_id"),
                    "message": user_message,
                    "error_type": (safe_event.get("error") or {}).get("error_type")
                    if isinstance(safe_event.get("error"), dict)
                    else None,
                    "recorded_at": safe_event.get("recorded_at"),
                }
            )
    else:
        manifest.setdefault("degraded", False)

    outputs = safe_event.get("outputs") or {}
    if isinstance(outputs, dict) and outputs.get("output_path"):
        manifest.setdefault("final_outputs", [])
        manifest["final_outputs"].append(outputs)

    _atomic_json_write(manifest_path, manifest)
    return manifest_path


def update_manifest_fields(
    *,
    outputs_dir: str | Path,
    session_id: str,
    fields: dict[str, Any],
) -> Path:
    session_dir = Path(outputs_dir) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = session_dir / "run_manifest.json"
    manifest = {}
    if manifest_path.exists() and manifest_path.stat().st_size > 0:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("session_id", session_id)
    manifest.setdefault("created_at", utc_now_iso())
    manifest["updated_at"] = utc_now_iso()
    manifest.update(mask_secrets(fields))
    _atomic_json_write(manifest_path, manifest)
    return manifest_path


def _atomic_json_write(path: Path, data: Any) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def _looks_like_secret(value: str) -> bool:
    s = value.strip()
    if len(s) < 20:
        return False
    prefixes = ("sk-", "ghp_", "gho_", "github_pat_", "xoxb-", "AKIA")
    return s.startswith(prefixes)


def _mask_secret_string(value: str) -> str:
    s = value.strip()
    if len(s) <= 8:
        return "***"
    return f"{s[:4]}***{s[-4:]}"

from __future__ import annotations

from pathlib import Path
from typing import Any


RETRYABLE_HTTP_STATUS = {408, 425, 429, 500, 502, 503, 504}


def classify_exception(exc: BaseException) -> str:
    name = type(exc).__name__.lower()
    text = str(exc).lower()

    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status in RETRYABLE_HTTP_STATUS:
        return "api_retryable"
    if "timeout" in name or "timeout" in text or "rate limit" in text or "429" in text:
        return "api_retryable"
    if "json" in name or "parse" in text or "unable to parse" in text:
        return "model_output_parse"
    if isinstance(exc, (FileNotFoundError, NotADirectoryError, PermissionError)):
        return "file_or_permission"
    if "api key" in text or "missing required field" in text or "not configured" in text:
        return "configuration"
    if "ffmpeg" in text or "moviepy" in text or "write_videofile" in text:
        return "render_failure"
    if "validation" in name or "schema" in text:
        return "schema_validation"
    return "unexpected"


def is_recoverable_error(error_type: str) -> bool:
    return error_type in {
        "api_retryable",
        "model_output_parse",
        "render_failure",
        "unexpected",
    }


def build_error_record(
    *,
    node_id: str,
    artifact_id: str,
    exc: BaseException,
    recoverable: bool | None = None,
    suggestion: str | None = None,
    input_artifacts: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error_type = classify_exception(exc)
    if recoverable is None:
        recoverable = is_recoverable_error(error_type)

    record: dict[str, Any] = {
        "node_id": node_id,
        "artifact_id": artifact_id,
        "error_type": error_type,
        "recoverable": bool(recoverable),
        "message": str(exc),
        "exception": type(exc).__name__,
        "suggestion": suggestion or suggestion_for_error(error_type, node_id),
        "input_artifacts": input_artifacts or [],
    }
    if extra:
        record["extra"] = extra
    return record


def suggestion_for_error(error_type: str, node_id: str) -> str:
    if node_id == "render_video":
        return (
            "Check the plan_timeline artifact, media paths, codec settings, and "
            "retry with a smaller output_max_dimension_px or a higher crf value."
        )
    if error_type == "api_retryable":
        return "Retry later, reduce request size, or check provider rate limits and network connectivity."
    if error_type == "model_output_parse":
        return "Retry the node with stricter JSON output instructions or use the default fallback output."
    if error_type == "configuration":
        return "Check config.local.toml or environment variables for the missing provider fields."
    if error_type == "file_or_permission":
        return "Check that referenced files exist, are readable, and output directories are writable."
    if error_type == "render_failure":
        return "Check the failing media segment, timeline window, and FFmpeg/MoviePy parameters."
    return "Inspect run_manifest.json and export a debug bundle for reproduction."


def sanitize_path_for_report(path: Any) -> str:
    if path is None:
        return ""
    try:
        return str(Path(path))
    except Exception:
        return str(path)


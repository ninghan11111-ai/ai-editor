from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json


DEFAULT_UNKNOWN_LICENSE = {
    "license": "unknown",
    "license_url": "",
    "commercial_allowed": False,
    "attribution_required": True,
    "compliance_notes": "License metadata is missing. Verify rights before commercial use.",
}


def generate_license_report(
    *,
    session_dir: str | Path,
    session_id: str,
    repo_root: str | Path | None = None,
) -> tuple[Path, Path]:
    session_path = Path(session_dir)
    repo_root_path = Path(repo_root or ".").resolve()
    artifacts = _load_session_artifacts(session_path)

    assets: list[dict[str, Any]] = []
    assets.extend(_assets_from_load_media(artifacts))
    assets.extend(_assets_from_search_media(artifacts))
    assets.extend(_assets_from_bgm(artifacts, repo_root_path))
    assets.extend(_assets_from_text_rec(artifacts, repo_root_path))
    assets.extend(_assets_from_ai_transition(artifacts))

    report = {
        "schema_version": 1,
        "session_id": session_id,
        "asset_count": len(assets),
        "assets": assets,
        "disclaimer": (
            "This report records available provenance metadata. It is not legal advice. "
            "Users must verify people, trademarks, music, fonts, generated media, and uploaded assets before commercial use."
        ),
    }

    json_path = session_path / "license_report.json"
    md_path = session_path / "license_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    return json_path, md_path


def _load_session_artifacts(session_path: Path) -> dict[str, list[Any]]:
    meta_path = session_path / "meta.json"
    if not meta_path.exists():
        return {}
    try:
        metas = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    out: dict[str, list[Any]] = {}
    for meta in metas or []:
        if not isinstance(meta, dict):
            continue
        node_id = meta.get("node_id")
        path = meta.get("path")
        if not node_id or not path:
            continue
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            continue
        payload = data.get("payload") if isinstance(data, dict) else None
        out.setdefault(str(node_id), []).append(payload)
    return out


def _assets_from_load_media(artifacts: dict[str, list[Any]]) -> list[dict[str, Any]]:
    assets = []
    for payload in artifacts.get("load_media", []):
        if not isinstance(payload, dict):
            continue
        for item in payload.get("media", []) or []:
            if not isinstance(item, dict):
                continue
            path = str(item.get("orig_path") or item.get("path") or "")
            assets.append(
                _asset(
                    asset_type="media",
                    source="user_upload_or_local",
                    path=path,
                    media_type=item.get("media_type"),
                    extra={
                        "media_id": item.get("media_id"),
                        "metadata": item.get("metadata"),
                        "user_confirmed_rights": "unknown",
                    },
                )
            )
    return assets


def _assets_from_search_media(artifacts: dict[str, list[Any]]) -> list[dict[str, Any]]:
    assets = []
    for payload in artifacts.get("search_media", []):
        if not isinstance(payload, dict):
            continue
        for item in payload.get("search_media", []) or []:
            path = item.get("path") if isinstance(item, dict) else item
            assets.append(
                _asset(
                    asset_type="media",
                    source="pexels",
                    path=path,
                    license="Pexels License",
                    license_url="https://www.pexels.com/license/",
                    commercial_allowed=True,
                    attribution_required=False,
                    compliance_notes=(
                        "Pexels media may still contain people, trademarks, brands, or copyrighted works. "
                        "Verify rights for the final use case."
                    ),
                )
            )
    return assets


def _assets_from_bgm(artifacts: dict[str, list[Any]], repo_root: Path) -> list[dict[str, Any]]:
    bgm_meta = _load_json_list(repo_root / "resource/bgms/meta.json")
    by_path = {str(item.get("path")): item for item in bgm_meta if isinstance(item, dict)}
    assets = []
    for payload in artifacts.get("select_bgm", []):
        if not isinstance(payload, dict):
            continue
        bgm = payload.get("bgm") or {}
        if not isinstance(bgm, dict) or not bgm.get("path"):
            continue
        info = by_path.get(str(bgm.get("path"))) or by_path.get(_relative_resource_path(bgm.get("path"))) or {}
        assets.append(
            _asset(
                asset_type="bgm",
                source="builtin_resource",
                path=bgm.get("path"),
                license=info.get("license"),
                license_url=info.get("license_url"),
                commercial_allowed=info.get("commercial_allowed"),
                attribution_required=info.get("attribution_required"),
                compliance_notes=info.get("compliance_notes"),
                extra={"bgm_id": bgm.get("bgm_id")},
            )
        )
    return assets


def _assets_from_text_rec(artifacts: dict[str, list[Any]], repo_root: Path) -> list[dict[str, Any]]:
    font_meta = _load_json_list(repo_root / "resource/fonts/font_info.json")
    by_name = {str(item.get("font_name")): item for item in font_meta if isinstance(item, dict)}
    assets = []
    for payload in artifacts.get("elementrec_text", []):
        candidates = payload if isinstance(payload, list) else payload.get("text_rec", payload) if isinstance(payload, dict) else []
        if isinstance(candidates, dict):
            candidates = [candidates]
        for item in candidates or []:
            if not isinstance(item, dict):
                continue
            info = by_name.get(str(item.get("font_name"))) or {}
            assets.append(
                _asset(
                    asset_type="font",
                    source="builtin_resource",
                    path=info.get("font_path"),
                    license=info.get("license"),
                    license_url=info.get("license_url"),
                    commercial_allowed=info.get("commercial_allowed"),
                    attribution_required=info.get("attribution_required"),
                    compliance_notes=info.get("compliance_notes"),
                    extra={"font_name": item.get("font_name")},
                )
            )
    return assets


def _assets_from_ai_transition(artifacts: dict[str, list[Any]]) -> list[dict[str, Any]]:
    assets = []
    for payload in artifacts.get("generate_ai_transition", []):
        if not isinstance(payload, dict):
            continue
        transition_info = payload.get("transition_info") or {}
        if not isinstance(transition_info, dict):
            continue
        for transition_id, item in transition_info.items():
            if not isinstance(item, dict):
                continue
            assets.append(
                _asset(
                    asset_type="ai_generated_transition",
                    source="ai_generated",
                    path=item.get("path"),
                    license="provider_terms",
                    commercial_allowed="unknown",
                    attribution_required="unknown",
                    compliance_notes="Check the selected video generation provider terms before commercial use.",
                    extra={"transition_id": transition_id},
                )
            )
    return assets


def _asset(
    *,
    asset_type: str,
    source: str,
    path: Any,
    license: Any = None,
    license_url: Any = None,
    commercial_allowed: Any = None,
    attribution_required: Any = None,
    compliance_notes: Any = None,
    media_type: Any = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path_s = str(path or "")
    defaults = DEFAULT_UNKNOWN_LICENSE
    return {
        "asset_id": _asset_id(asset_type, source, path_s),
        "asset_type": asset_type,
        "source": source,
        "path": path_s,
        "media_type": media_type,
        "file_sha256": _sha256_if_exists(path_s),
        "license": license if license not in (None, "") else defaults["license"],
        "license_url": license_url if license_url not in (None, "") else defaults["license_url"],
        "commercial_allowed": commercial_allowed if commercial_allowed not in (None, "") else defaults["commercial_allowed"],
        "attribution_required": attribution_required if attribution_required not in (None, "") else defaults["attribution_required"],
        "compliance_notes": compliance_notes if compliance_notes not in (None, "") else defaults["compliance_notes"],
        "extra": extra or {},
    }


def _asset_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _sha256_if_exists(path: str) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists() or not p.is_file():
        return ""
    h = hashlib.sha256()
    try:
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _relative_resource_path(path: Any) -> str:
    s = str(path or "")
    marker = "resource/"
    if marker in s:
        return "./" + s[s.index(marker):]
    return s


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# License Report",
        "",
        f"- Session: `{report.get('session_id')}`",
        f"- Assets: {report.get('asset_count', 0)}",
        "",
        "> This report records provenance metadata only. Verify rights before commercial use.",
        "",
        "| Asset | Source | License | Commercial | Attribution | Path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for asset in report.get("assets", []):
        lines.append(
            "| {asset_type} | {source} | {license} | {commercial} | {attr} | `{path}` |".format(
                asset_type=asset.get("asset_type", ""),
                source=asset.get("source", ""),
                license=asset.get("license", ""),
                commercial=asset.get("commercial_allowed", ""),
                attr=asset.get("attribution_required", ""),
                path=str(asset.get("path", "")).replace("|", "\\|"),
            )
        )
    lines.append("")
    return "\n".join(lines)

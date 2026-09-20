from __future__ import annotations

from pathlib import Path
from typing import Any


FALLBACK_NODE_IDS = {
    "search_media",
    "understand_clips",
    "filter_clips",
    "group_clips",
    "generate_script",
    "generate_voiceover",
    "select_bgm",
    "generate_ai_transition",
    "elementrec_transition",
    "elementrec_text",
    "script_template_rec",
    "local_asr",
    "speech_rough_cut",
}


FALLBACK_MESSAGES = {
    "search_media": {
        "en": "Media search failed. AI Editor continued with uploaded or local media.",
        "zh": "素材搜索失败，已继续使用用户上传或本地素材。",
    },
    "understand_clips": {
        "en": "Clip understanding failed. AI Editor used filenames, duration, and basic metadata for rough captions.",
        "zh": "画面理解失败，已使用文件名、时长和基础元信息生成粗略说明。",
    },
    "filter_clips": {
        "en": "Clip filtering failed. AI Editor kept the available clips in their current order.",
        "zh": "素材筛选失败，已保留可用素材并按当前顺序继续。",
    },
    "group_clips": {
        "en": "Clip grouping failed. AI Editor placed available clips into a default group.",
        "zh": "素材分组失败，已将可用素材放入默认分组继续。",
    },
    "generate_script": {
        "en": "Script generation failed. AI Editor generated simple fallback subtitles.",
        "zh": "脚本生成失败，已生成简单兜底字幕。",
    },
    "generate_voiceover": {
        "en": "Voiceover generation failed. AI Editor continued in subtitle-only mode.",
        "zh": "配音生成失败，已改为字幕-only 模式继续。",
    },
    "select_bgm": {
        "en": "BGM selection failed. AI Editor continued without background music.",
        "zh": "背景音乐选择失败，已改为无 BGM 继续。",
    },
    "generate_ai_transition": {
        "en": "AI transition generation failed. AI Editor used normal cuts or default transitions.",
        "zh": "AI 转场生成失败，已改用普通硬切或默认转场。",
    },
    "elementrec_transition": {
        "en": "Transition recommendation failed. AI Editor continued without recommended transitions.",
        "zh": "转场推荐失败，已跳过推荐转场继续。",
    },
    "elementrec_text": {
        "en": "Text style recommendation failed. AI Editor used the default font style.",
        "zh": "文字样式推荐失败，已使用默认字体样式。",
    },
    "script_template_rec": {
        "en": "Script template recommendation failed. AI Editor continued without a template.",
        "zh": "脚本模板推荐失败，已跳过模板继续。",
    },
    "local_asr": {
        "en": "Local ASR failed. AI Editor continued without speech recognition results.",
        "zh": "本地语音识别失败，已跳过 ASR 结果继续。",
    },
    "speech_rough_cut": {
        "en": "Speech rough cut failed. AI Editor continued with the original detected shots.",
        "zh": "语音粗剪失败，已使用原始切分镜头继续。",
    },
}


def should_fallback_node(node_id: str) -> bool:
    return node_id in FALLBACK_NODE_IDS


def fallback_user_message(node_id: str, lang: str | None = None) -> str:
    messages = FALLBACK_MESSAGES.get(node_id)
    if not messages:
        return "Optional processing failed. AI Editor used a fallback result."
    lang_key = "zh" if str(lang or "").lower().startswith("zh") else "en"
    return messages.get(lang_key) or messages["en"]


def build_fallback_payload(node_id: str, inputs: dict[str, Any]) -> dict[str, Any] | list[Any] | None:
    if node_id == "search_media":
        return {"search_media": []}
    if node_id == "understand_clips":
        return _fallback_understand_clips(inputs)
    if node_id == "filter_clips":
        return _fallback_filter_clips(inputs)
    if node_id == "group_clips":
        selected = (inputs.get("filter_clips") or {}).get("selected") or _clip_ids(inputs)
        return {"groups": _single_group(selected)}
    if node_id == "generate_script":
        return _fallback_generate_script(inputs)
    if node_id == "generate_voiceover":
        return {"voiceover": []}
    if node_id == "select_bgm":
        return {"bgm": {}}
    if node_id == "generate_ai_transition":
        return inputs.get("group_clips", {}) or {"groups": _single_group(_clip_ids(inputs))}
    if node_id == "elementrec_transition":
        return []
    if node_id == "elementrec_text":
        return [{"font_name": "SiYuanHeiTi", "font_color": (255, 255, 255, 255)}]
    if node_id == "script_template_rec":
        return {}
    if node_id == "local_asr":
        return {"asr": []}
    if node_id == "speech_rough_cut":
        return inputs.get("split_shots", {}) or {"clips": []}
    return None


def _clip_ids(inputs: dict[str, Any]) -> list[str]:
    clips = (inputs.get("split_shots") or {}).get("clips") or []
    return [str(c.get("clip_id")) for c in clips if isinstance(c, dict) and c.get("clip_id")]


def _single_group(clip_ids: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "group_id": "group_0001",
            "summary": "Fallback group preserving the original clip order.",
            "clip_ids": clip_ids,
        }
    ] if clip_ids else []


def _fallback_understand_clips(inputs: dict[str, Any]) -> dict[str, Any]:
    media_by_id = {}
    for item in (inputs.get("load_media") or {}).get("media", []) or []:
        if isinstance(item, dict) and item.get("media_id"):
            media_by_id[str(item["media_id"])] = item

    clip_captions: list[dict[str, Any]] = []
    for clip in (inputs.get("split_shots") or {}).get("clips", []) or []:
        if not isinstance(clip, dict):
            continue
        source_ref = clip.get("source_ref") or {}
        media_id = str(source_ref.get("media_id", "") or "")
        media = media_by_id.get(media_id, {})
        path = media.get("path") or clip.get("path") or media.get("orig_path") or ""
        metadata = media.get("metadata") or {}
        duration = source_ref.get("duration") or metadata.get("duration") or 0
        basename = Path(str(path)).name if path else media_id or "unknown media"
        clip_captions.append(
            {
                "clip_id": clip.get("clip_id", ""),
                "caption": (
                    f"Fallback caption for {basename}; "
                    f"type={clip.get('kind') or media.get('media_type', 'unknown')}; "
                    f"duration_ms={duration}."
                ),
                "source_ref": {"media_id": media_id},
                "fallback": True,
            }
        )

    return {
        "clip_captions": clip_captions,
        "overall": "Fallback visual summary generated from filenames and media metadata.",
    }


def _fallback_filter_clips(inputs: dict[str, Any]) -> dict[str, Any]:
    understand = inputs.get("understand_clips") or {}
    clip_captions = understand.get("clip_captions") or []
    selected = [c.get("clip_id") for c in clip_captions if isinstance(c, dict) and c.get("clip_id")]
    if not selected:
        selected = _clip_ids(inputs)
    return {"clip_captions": clip_captions, "selected": selected}


def _fallback_generate_script(inputs: dict[str, Any]) -> dict[str, Any]:
    groups = (inputs.get("group_clips") or {}).get("groups") or _single_group(_clip_ids(inputs))
    captions = {
        str(c.get("clip_id")): str(c.get("caption", "") or "")
        for c in (inputs.get("understand_clips") or {}).get("clip_captions", []) or []
        if isinstance(c, dict) and c.get("clip_id")
    }

    group_scripts: list[dict[str, Any]] = []
    subtitle_index = 1
    for group in groups:
        if not isinstance(group, dict):
            continue
        group_id = str(group.get("group_id") or f"group_{len(group_scripts) + 1:04d}")
        clip_ids = [str(x) for x in group.get("clip_ids", []) if x]
        text = _fallback_group_text(group, clip_ids, captions)
        units: list[dict[str, Any]] = []
        for index_in_group, part in enumerate(_split_text_units(text)):
            units.append(
                {
                    "unit_id": f"subtitle_{subtitle_index:04d}",
                    "index_in_group": index_in_group,
                    "text": part,
                }
            )
            subtitle_index += 1
        group_scripts.append(
            {
                "group_id": group_id,
                "raw_text": text,
                "subtitle_units": units,
            }
        )

    return {
        "group_scripts": group_scripts,
        "title": "Auto-generated fallback script",
    }


def _fallback_group_text(group: dict[str, Any], clip_ids: list[str], captions: dict[str, str]) -> str:
    summary = str(group.get("summary", "") or "").strip()
    caption = next((captions[cid] for cid in clip_ids if captions.get(cid)), "")
    base = caption or summary or "This shot continues the story in a clear visual sequence."
    return base[:120].strip()


def _split_text_units(text: str) -> list[str]:
    raw = str(text or "").replace("\n", " ").strip()
    if not raw:
        return ["This shot continues the story."]
    separators = "，,。.！!?？"
    parts: list[str] = []
    buf = ""
    for ch in raw:
        if ch in separators:
            if buf.strip():
                parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts or [raw]

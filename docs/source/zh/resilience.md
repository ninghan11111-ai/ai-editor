# 稳定性与可调试性

本文说明 AI Editor 的长链路容错、断点续跑和调试产物。

## 节点级 fallback

系统把节点分成两类：

- 必需节点：`load_media`、`split_shots`、`plan_timeline` / `plan_timeline_pro`、`render_video`
- 可降级节点：`search_media`、`understand_clips`、`generate_script`、`generate_voiceover`、`select_bgm`、`generate_ai_transition`、`elementrec_text`、`elementrec_transition`

可降级节点失败时，节点会返回 fallback artifact，并继续后续流程：

- `search_media` 失败：返回空搜索结果，继续使用用户上传素材。
- `understand_clips` 失败：用文件名、素材类型和时长生成粗略 caption。
- `generate_script` 失败：用分组摘要或 caption 生成简单字幕。
- `generate_voiceover` 失败：返回空配音，进入字幕-only 模式。
- `select_bgm` 失败：返回空 BGM，继续无音乐渲染。
- `generate_ai_transition` 失败：返回原始分组，使用普通硬切/默认转场。
- `elementrec_text` / `elementrec_transition` 失败：使用默认字体或无转场。

必需节点失败仍会中断当前任务，但会返回统一错误结构，便于定位。

## 降级提示

可降级节点失败不会中断最终渲染，但系统会把用户可读提示写入工具结果和 `run_manifest.json`：

```json
{
  "degraded": true,
  "warnings": [
    {
      "node_id": "generate_voiceover",
      "artifact_id": "generate_voiceover_...",
      "message": "配音生成失败，已改为字幕-only 模式继续。",
      "error_type": "api_retryable",
      "recorded_at": "2026-07-10T..."
    }
  ]
}
```

前端或调用方建议按以下规则展示：

- `render_video` 成功且 `degraded=true`：显示黄色 warning，例如“视频已生成，但部分 AI 功能已降级”。
- 必需节点失败或 `render_video` 失败：显示红色错误。
- `degraded=false`：显示普通成功状态。

## 统一错误格式

节点错误会写入工具结果中的 `error` 字段，格式如下：

```json
{
  "node_id": "generate_voiceover",
  "artifact_id": "generate_voiceover_...",
  "error_type": "configuration",
  "recoverable": false,
  "message": "provider=minimax missing required field: api_key",
  "exception": "ValueError",
  "suggestion": "Check config.local.toml or environment variables for the missing provider fields.",
  "input_artifacts": []
}
```

常见 `error_type`：

- `api_retryable`：超时、429、5xx 等，可重试。
- `model_output_parse`：模型输出 JSON 不合格。
- `configuration`：配置或密钥缺失。
- `file_or_permission`：文件不存在或权限不足。
- `render_failure`：FFmpeg/MoviePy 渲染失败。
- `unexpected`：未分类异常。

## run_manifest.json

每个 session 会自动生成：

```text
outputs/<session_id>/run_manifest.json
```

它记录：

- 每个节点的 `node_id`、`artifact_id`、`tool_call_id`
- 节点状态：`success`、`fallback`、`failed`
- 是否降级：`degraded`
- 给用户看的降级提示：`warnings`
- 错误结构
- artifact 路径
- 输出摘要
- 最终视频路径
- license report 路径

排查问题时先看 `run_manifest.json`，再看失败节点对应的 artifact JSON。

## Debug Bundle

导出调试包：

```bash
PYTHONPATH=src python scripts/export_debug_bundle.py --session <session_id>
```

默认输出：

```text
debug_bundles/debug_bundle_<session_id>.zip
```

调试包包含：

- `run_manifest.json`
- `session_state.json`
- 节点 JSON 产物
- `license_report.json/md`
- 已脱敏的配置摘要

默认不包含视频、音频、图片等媒体文件。如确实需要复现媒体问题，可加：

```bash
PYTHONPATH=src python scripts/export_debug_bundle.py --session <session_id> --include-media
```

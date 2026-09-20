# Resilience and Debugging

AI Editor now records each node run and keeps optional failures from breaking the full render path.

## Node fallback

Required nodes still fail the run when they cannot complete:

- `load_media`
- `split_shots`
- `plan_timeline` / `plan_timeline_pro`
- `render_video`

Optional or high-risk nodes return fallback artifacts:

- `search_media`: empty search result; uploaded media is still used.
- `understand_clips`: captions from filename, media type, and duration.
- `generate_script`: simple subtitle text from group summaries or captions.
- `generate_voiceover`: empty voiceover, subtitle-only mode.
- `select_bgm`: empty BGM, render without music.
- `generate_ai_transition`: original groups, normal cuts/default transitions.
- `elementrec_text` / `elementrec_transition`: default font or no transition.

## Degradation warnings

Fallback keeps the render path alive, but it is not silent. Each fallback result includes a user-facing message, and `run_manifest.json` aggregates those messages:

```json
{
  "degraded": true,
  "warnings": [
    {
      "node_id": "generate_voiceover",
      "artifact_id": "generate_voiceover_...",
      "message": "Voiceover generation failed. AI Editor continued in subtitle-only mode.",
      "error_type": "api_retryable",
      "recorded_at": "2026-07-10T..."
    }
  ]
}
```

Recommended UI behavior:

- Render succeeded and `degraded=true`: show a yellow warning such as "Video generated, but some AI features were degraded."
- Required node or `render_video` failed: show a red error.
- `degraded=false`: show normal success.

## run_manifest.json

Each session writes:

```text
outputs/<session_id>/run_manifest.json
```

It records node status, artifact ids, errors, fallback use, user-facing degradation warnings, output summaries, final video paths, and license report paths.

## Debug bundle

Export a masked debug bundle:

```bash
PYTHONPATH=src python scripts/export_debug_bundle.py --session <session_id>
```

Media files are excluded by default. Add `--include-media` only when the media itself is needed for reproduction.

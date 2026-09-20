# Security and Compliance

## Keep secrets out of config.toml

Keep `config.toml` safe to commit. Put local API keys in:

```bash
cp config.local.toml.example config.local.toml
```

`config.local.toml` is ignored by Git and overrides `config.toml`.

Environment variables override both config files:

```bash
export OPENSTORYLINE_LLM_API_KEY="..."
export OPENSTORYLINE_VLM_API_KEY="..."
export PEXELS_API_KEY="..."
export TTS_MINIMAX_API_KEY="..."
export AI_TRANSITION_MINIMAX_API_KEY="..."
```

## Secret scanning

Run manually:

```bash
python scripts/check_secrets.py
python scripts/check_secrets.py --all
```

Enable pre-commit:

```bash
pip install pre-commit
pre-commit install
```

For GitHub repositories, enable Secret scanning, Push protection, and Dependabot alerts.

## License report

After a successful render, AI Editor writes:

```text
outputs/<session_id>/license_report.json
outputs/<session_id>/license_report.md
```

The report records available provenance for uploaded/local media, Pexels media, bundled BGM, bundled fonts, and AI transitions.

It is not legal advice. Always verify rights before commercial use.

## Bundled resource metadata

Downloaded resources live under `resource/` and are usually ignored by Git. After downloading resources, annotate metadata with:

```bash
python scripts/annotate_resource_licenses.py
```

Unknown licenses default to `commercial_allowed=false`.


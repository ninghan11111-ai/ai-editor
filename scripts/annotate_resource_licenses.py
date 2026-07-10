#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


RESOURCE_META_FILES = [
    Path("resource/bgms/meta.json"),
    Path("resource/fonts/font_info.json"),
    Path("resource/script_templates/meta.json"),
]

DEFAULT_LICENSE_FIELDS = {
    "license": "unknown",
    "license_url": "",
    "commercial_allowed": False,
    "attribution_required": True,
    "compliance_notes": (
        "License metadata was not provided with the bundled resource. "
        "Verify rights before commercial use."
    ),
}


def main() -> int:
    changed_files = []
    for path in RESOURCE_META_FILES:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            continue
        changed = False
        for item in data:
            if not isinstance(item, dict):
                continue
            for key, value in DEFAULT_LICENSE_FIELDS.items():
                if key not in item:
                    item[key] = value
                    changed = True
        if changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed_files.append(str(path))

    for path in changed_files:
        print(f"updated {path}")
    if not changed_files:
        print("resource license metadata already present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


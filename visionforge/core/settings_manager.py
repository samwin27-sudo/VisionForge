from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

SETTINGS_DIR = Path.home() / ".visionforge"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "default_yolo_model": "",
    "default_segmentation_model": "",
    "default_sam_model_type": "auto",
    "default_device": "auto",
    "last_autolabel_mapping": "",
}


def load_user_settings() -> Dict[str, Any]:
    if not SETTINGS_FILE.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data if isinstance(data, dict) else {})
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_user_settings(settings: Dict[str, Any]) -> Path:
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    merged = load_user_settings()
    merged.update(settings)
    SETTINGS_FILE.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return SETTINGS_FILE

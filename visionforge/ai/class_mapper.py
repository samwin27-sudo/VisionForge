from __future__ import annotations

import json
from typing import Dict

DEFAULT_MAPPING_TEXT = """# VisionForge class mapping example
# Format: ProjectClass = model_class_1, model_class_2

Vehicle = car, truck, bus, train
Bike = motorcycle, bicycle, cycle
Pedestrian = person
Road Signage = traffic light, stop sign, traffic sign
Road Damage = pothole
Road Feature = speedbreaker, speed breaker
"""


def parse_mapping_text(text: str) -> Dict[str, str]:
    """Return mapping from model class name -> project class name.

    Supports both:
        Vehicle = car, truck, bus
    and JSON:
        {"Vehicle": ["car", "truck", "bus"]}
    """
    text = (text or "").strip()
    if not text:
        return {}

    # JSON mode: project class -> list/string model classes
    if text.startswith("{"):
        data = json.loads(text)
        out: Dict[str, str] = {}
        for project_class, model_classes in data.items():
            if isinstance(model_classes, str):
                model_classes = [model_classes]
            for model_class in model_classes:
                key = str(model_class).strip()
                if key:
                    out[key] = str(project_class).strip()
        return out

    out: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        project_class, model_part = line.split("=", 1)
        project_class = project_class.strip()
        for model_class in model_part.split(","):
            key = model_class.strip()
            if key and project_class:
                out[key] = project_class
    return out


def mapping_to_project_groups(mapping: Dict[str, str]) -> Dict[str, list[str]]:
    groups: Dict[str, list[str]] = {}
    for model_class, project_class in mapping.items():
        groups.setdefault(project_class, []).append(model_class)
    return groups

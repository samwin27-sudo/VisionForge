from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import numpy as np

from visionforge.ai.segmentation_backend import SegmentationBackend, MissingSegmentationDependency


@dataclass
class SamSettings:
    checkpoint_path: str
    model_type: str = "auto"
    device: str = "auto"


def detect_sam_model_type(checkpoint_path: str, requested: str = "auto") -> str:
    if requested and requested != "auto":
        return requested
    name = Path(checkpoint_path).name.lower()
    if "vit_h" in name or "4b8939" in name:
        return "vit_h"
    if "vit_l" in name or "0b3195" in name:
        return "vit_l"
    return "vit_b"


def resolve_device(device: str) -> str:
    if device and device != "auto":
        return device
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


class SamSegmenter(SegmentationBackend):
    def __init__(self, settings: SamSettings):
        self.settings = settings
        self._predictor = None
        self._cv2 = None
        self._last_image = None
        self.model_type = detect_sam_model_type(settings.checkpoint_path, settings.model_type)
        self.device = resolve_device(settings.device)

    def _load_predictor(self):
        if self._predictor is not None:
            return self._predictor
        try:
            import cv2
            from segment_anything import SamPredictor, sam_model_registry
        except ImportError as exc:
            raise MissingSegmentationDependency(
                "Segmentation assistant is not available. Install segmentation dependencies using: "
                "pip install -r requirements-segmentation.txt"
            ) from exc

        ckpt = Path(self.settings.checkpoint_path).expanduser()
        if not ckpt.exists():
            raise FileNotFoundError(f"SAM checkpoint not found: {ckpt}")

        if self.model_type not in sam_model_registry:
            raise ValueError(f"Unsupported SAM model type: {self.model_type}. Use auto, vit_b, vit_l, or vit_h.")

        sam = sam_model_registry[self.model_type](checkpoint=str(ckpt))
        sam.to(device=self.device)
        self._cv2 = cv2
        self._predictor = SamPredictor(sam)
        return self._predictor

    def _set_image(self, image_path):
        pred = self._load_predictor()
        p = Path(image_path)
        if self._last_image == p:
            return
        img = self._cv2.imread(str(p))
        if img is None:
            raise FileNotFoundError(f"Could not read image for SAM: {p}")
        pred.set_image(self._cv2.cvtColor(img, self._cv2.COLOR_BGR2RGB))
        self._last_image = p

    def segment_from_box(self, image_path, bbox_xyxy):
        self._set_image(image_path)
        pred = self._load_predictor()
        box = np.array(bbox_xyxy, dtype=np.float32)
        masks, scores, _ = pred.predict(box=box, multimask_output=True)
        if masks is None or len(masks) == 0:
            return np.zeros((1, 1), dtype=bool)
        best = int(np.argmax(scores)) if scores is not None and len(scores) else 0
        return masks[best].astype(bool)

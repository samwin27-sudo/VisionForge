from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from visionforge.core.annotation_store import Annotation
from visionforge.core.bbox_utils import clamp_bbox


class MissingYoloDependency(RuntimeError):
    pass


@dataclass
class YoloSettings:
    model_path: str
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    image_size: int = 640
    device: str = "auto"
    auto_accept_threshold: Optional[float] = None
    save_predictions_immediately: bool = True


class YoloAutoLabeler:
    def __init__(self, settings: YoloSettings, class_mapping=None):
        self.settings = settings
        self.class_mapping = class_mapping or {}
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise MissingYoloDependency(
                "YOLO auto-labeling is not available. Install AI dependencies using: pip install -r requirements-ai.txt"
            ) from exc

        model_ref = (self.settings.model_path or "").strip()
        if not model_ref:
            raise FileNotFoundError("Select a YOLO .pt model first, or download one with scripts/download_yolo_models.py")

        p = Path(model_ref).expanduser()
        # If user gives a local path, require it. If user gives yolov8n.pt, let Ultralytics resolve/download.
        if ("/" in model_ref or "\\" in model_ref) and not p.exists():
            raise FileNotFoundError(f"YOLO model file not found: {p}")

        self._model = YOLO(str(p) if p.exists() else model_ref)
        return self._model

    def predict_image(self, image_path, project_class_lookup=None):
        model = self._load_model()
        device = None if self.settings.device == "auto" else self.settings.device
        results = model.predict(
            source=str(image_path),
            conf=self.settings.confidence_threshold,
            iou=self.settings.iou_threshold,
            imgsz=self.settings.image_size,
            device=device,
            verbose=False,
        )
        out = []
        if not results:
            return out
        r = results[0]
        names = getattr(r, "names", {}) or getattr(model, "names", {})
        h, w = int(r.orig_shape[0]), int(r.orig_shape[1])
        boxes = getattr(r, "boxes", None)
        if boxes is None:
            return out
        for box in boxes:
            xyxy = box.xyxy[0].detach().cpu().tolist()
            cls = int(box.cls[0].detach().cpu().item())
            conf = float(box.conf[0].detach().cpu().item())
            model_name = str(names.get(cls, cls))
            cname = self.class_mapping.get(model_name, model_name)
            cid = (project_class_lookup or {}).get(cname, cls)
            status = "accepted" if self.settings.auto_accept_threshold and conf >= self.settings.auto_accept_threshold else "pending"
            out.append(
                Annotation(
                    annotation_type="bbox",
                    bbox=clamp_bbox(xyxy, w, h),
                    class_name=cname,
                    class_id=int(cid),
                    confidence=conf,
                    source="yolo",
                    status=status,
                )
            )
        return out

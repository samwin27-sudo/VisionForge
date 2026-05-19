from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Annotation:
    annotation_id: str = field(default_factory=lambda: str(uuid4()))
    annotation_type: str = "bbox"
    bbox: Optional[List[float]] = None
    polygon: Optional[Any] = None
    mask_path: Optional[str] = None
    class_name: str = "object"
    class_id: int = 0
    confidence: Optional[float] = None
    source: str = "manual"
    status: str = "accepted"
    linked_annotation_id: Optional[str] = None
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    def touch(self): self.updated_at = now_iso()
    def to_dict(self) -> Dict[str, Any]: return asdict(self)
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Annotation":
        return cls(**{k:v for k,v in data.items() if k in cls.__dataclass_fields__})

@dataclass
class ImageRecord:
    filename: str
    relative_path: str
    width: int = 0
    height: int = 0
    annotations: List[Annotation] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    broken: bool = False
    def to_dict(self):
        d=asdict(self); d['annotations']=[a.to_dict() for a in self.annotations]; return d
    @classmethod
    def from_dict(cls, data):
        anns=[Annotation.from_dict(a) for a in data.get('annotations', [])]
        d={k:v for k,v in data.items() if k in cls.__dataclass_fields__}; d['annotations']=anns; return cls(**d)

@dataclass
class Project:
    project_name: str = "VisionForge Project"
    dataset_path: str = ""
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    class_groups: Dict[str, List[str]] = field(default_factory=dict)
    images: List[ImageRecord] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    split_info: Dict[str, Any] = field(default_factory=dict)
    augmentation_info: Dict[str, Any] = field(default_factory=dict)
    def touch(self): self.updated_at=now_iso()
    def to_dict(self):
        d=asdict(self); d['images']=[i.to_dict() for i in self.images]; return d
    @classmethod
    def from_dict(cls, data):
        imgs=[ImageRecord.from_dict(i) for i in data.get('images', [])]
        d={k:v for k,v in data.items() if k in cls.__dataclass_fields__}; d['images']=imgs; return cls(**d)

class AnnotationStore:
    def __init__(self, project: Optional[Project]=None): self.project=project or Project()
    @property
    def images(self): return self.project.images
    def set_dataset(self, dataset_path: str, image_records: Iterable[ImageRecord]):
        self.project.dataset_path=str(dataset_path); self.project.images=list(image_records); self.project.touch()
    def add_class(self, name: str, color: str="#00E5FF") -> int:
        name=name.strip() or 'object'
        existing=self.get_class_by_name(name)
        if existing is not None: return int(existing['id'])
        cid=len(self.project.classes); self.project.classes.append({'id':cid,'name':name,'color':color}); self.project.touch(); return cid
    def get_class_by_name(self, name): return next((c for c in self.project.classes if c['name']==name), None)
    def add_annotation(self, image_index: int, annotation: Annotation):
        self.project.images[image_index].annotations.append(annotation); self.project.touch(); return annotation
    def get_annotation(self, image_index: int, annotation_id: str):
        return next((a for a in self.project.images[image_index].annotations if a.annotation_id==annotation_id), None)
    def delete_annotation(self, image_index: int, annotation_id: str) -> bool:
        img=self.project.images[image_index]; n=len(img.annotations); img.annotations=[a for a in img.annotations if a.annotation_id!=annotation_id]; self.project.touch(); return len(img.annotations)!=n
    def accepted_annotations(self, image: ImageRecord): return [a for a in image.annotations if a.status=='accepted']
    def all_annotations(self, statuses=None):
        for img in self.project.images:
            for ann in img.annotations:
                if statuses is None or ann.status in statuses: yield img, ann
    def dataset_root(self): return Path(self.project.dataset_path)

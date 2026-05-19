from dataclasses import dataclass
from pathlib import Path
import numpy as np
from visionforge.ai.segmentation_backend import SegmentationBackend, MissingSegmentationDependency
@dataclass
class SamSettings:
    checkpoint_path: str
    model_type: str = 'vit_b'
    device: str = 'cpu'
class SamSegmenter(SegmentationBackend):
    def __init__(self, settings: SamSettings): self.settings=settings; self._predictor=None; self._cv2=None; self._last=None
    def _load_predictor(self):
        if self._predictor is not None: return self._predictor
        try:
            import cv2
            from segment_anything import SamPredictor, sam_model_registry
        except ImportError as exc:
            raise MissingSegmentationDependency('Segmentation assistant is not available. Install segmentation dependencies using pip install -r requirements-segmentation.txt') from exc
        ckpt=Path(self.settings.checkpoint_path)
        if not ckpt.exists(): raise FileNotFoundError(f'SAM checkpoint not found: {ckpt}')
        sam=sam_model_registry[self.settings.model_type](checkpoint=str(ckpt)); sam.to(device=self.settings.device)
        self._cv2=cv2; self._predictor=SamPredictor(sam); return self._predictor
    def _set_image(self, image_path):
        pred=self._load_predictor(); p=Path(image_path)
        if self._last==p: return
        img=self._cv2.imread(str(p))
        if img is None: raise FileNotFoundError(f'Could not read image: {p}')
        pred.set_image(self._cv2.cvtColor(img,self._cv2.COLOR_BGR2RGB)); self._last=p
    def segment_from_box(self, image_path, bbox_xyxy):
        self._set_image(image_path); pred=self._load_predictor(); masks,scores,_=pred.predict(box=np.array(bbox_xyxy,dtype=np.float32), multimask_output=True)
        if masks is None or len(masks)==0: return np.zeros((1,1),dtype=bool)
        return masks[int(np.argmax(scores))].astype(bool)

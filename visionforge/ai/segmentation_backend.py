from abc import ABC, abstractmethod
class MissingSegmentationDependency(RuntimeError): pass
class SegmentationBackend(ABC):
    @abstractmethod
    def segment_from_box(self, image_path, bbox_xyxy): ...
    def masks_from_boxes(self, image_path, boxes): return [self.segment_from_box(image_path,b) for b in boxes]

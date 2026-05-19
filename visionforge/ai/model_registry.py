from dataclasses import dataclass
@dataclass
class BackendInfo:
    name: str; description: str; available: bool; install_hint: str

def is_module_available(module_name: str) -> bool:
    try: __import__(module_name); return True
    except Exception: return False

def available_backends():
    return {
        'yolo': BackendInfo('Ultralytics YOLO','Object detection auto-labeling backend',is_module_available('ultralytics'),'pip install -r requirements-ai.txt'),
        'sam': BackendInfo('Segment Anything','Box-prompted segmentation backend',is_module_available('segment_anything'),'pip install -r requirements-segmentation.txt')
    }

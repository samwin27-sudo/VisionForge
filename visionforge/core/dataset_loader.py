from pathlib import Path
from PIL import Image, UnidentifiedImageError
from visionforge.config import SUPPORTED_IMAGE_EXTENSIONS
from visionforge.core.annotation_store import ImageRecord

def find_images(dataset_dir):
    root=Path(dataset_dir)
    if not root.exists(): raise FileNotFoundError(f"Dataset folder does not exist: {root}")
    return sorted([p for p in root.rglob('*') if p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS], key=lambda p: str(p.relative_to(root)).lower())

def read_image_size(path):
    try:
        with Image.open(path) as im: return int(im.width), int(im.height), False
    except (OSError, UnidentifiedImageError): return 0,0,True

def load_dataset(dataset_dir):
    root=Path(dataset_dir).resolve(); records=[]
    for p in find_images(root):
        w,h,broken=read_image_size(p)
        records.append(ImageRecord(filename=p.name, relative_path=str(p.relative_to(root)), width=w, height=h, broken=broken))
    return records

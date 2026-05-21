from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import math
import random

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from visionforge.core.annotation_store import Project
from visionforge.core.bbox_utils import clamp_bbox
from visionforge.core.project_io import save_project


def _flip_bbox_horizontal(bbox, image_width):
    x1, y1, x2, y2 = bbox
    return [image_width - x2, y1, image_width - x1, y2]


def _flip_bbox_vertical(bbox, image_height):
    x1, y1, x2, y2 = bbox
    return [x1, image_height - y2, x2, image_height - y1]


def _resize_bbox(bbox, sx, sy):
    x1, y1, x2, y2 = bbox
    return [x1 * sx, y1 * sy, x2 * sx, y2 * sy]


def _rotate_point(x, y, cx, cy, angle_rad):
    dx, dy = x - cx, y - cy
    ca, sa = math.cos(angle_rad), math.sin(angle_rad)
    return cx + dx * ca - dy * sa, cy + dx * sa + dy * ca


def _rotate_bbox(bbox, width, height, degrees):
    x1, y1, x2, y2 = bbox
    cx, cy = width / 2.0, height / 2.0
    # PIL positive angle is counter-clockwise in image coordinates; bbox approximation is conservative.
    angle = math.radians(-degrees)
    corners = [_rotate_point(x, y, cx, cy, angle) for x, y in [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]]
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return clamp_bbox([min(xs), min(ys), max(xs), max(ys)], width, height)


def _random_crop_image_and_bboxes(image, record, min_scale=0.80):
    w, h = image.size
    crop_scale = random.uniform(min_scale, 1.0)
    cw, ch = int(w * crop_scale), int(h * crop_scale)
    if cw >= w or ch >= h:
        return image, record
    left = random.randint(0, w - cw)
    top = random.randint(0, h - ch)
    right = left + cw
    bottom = top + ch
    image = image.crop((left, top, right, bottom))
    kept = []
    for ann in record.annotations:
        if not ann.bbox:
            continue
        x1, y1, x2, y2 = ann.bbox
        ix1, iy1 = max(x1, left), max(y1, top)
        ix2, iy2 = min(x2, right), min(y2, bottom)
        if ix2 <= ix1 or iy2 <= iy1:
            continue
        original_area = max(1.0, (x2 - x1) * (y2 - y1))
        visible_area = (ix2 - ix1) * (iy2 - iy1)
        if visible_area / original_area < 0.30:
            continue
        ann.bbox = [ix1 - left, iy1 - top, ix2 - left, iy2 - top]
        ann.polygon = None
        ann.mask_path = None
        if ann.annotation_type != "bbox":
            ann.annotation_type = "bbox"
        ann.touch()
        kept.append(ann)
    record.annotations = kept
    record.width, record.height = cw, ch
    return image, record


def _add_noise(image):
    arr = np.asarray(image).astype(np.int16)
    noise = np.random.normal(0, random.uniform(4, 14), arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _drop_segmentation_if_unsafe(record):
    for ann in record.annotations:
        if ann.polygon or ann.mask_path:
            ann.polygon = None
            ann.mask_path = None
            ann.annotation_type = "bbox"
            ann.source = ann.source + "+aug_bbox_only" if "aug_bbox_only" not in ann.source else ann.source
            ann.touch()


def augment_project(
    project,
    output_dir,
    copies_per_image=1,
    horizontal_flip=True,
    vertical_flip=False,
    brightness=True,
    contrast=False,
    grayscale=False,
    blur=False,
    noise=False,
    sharpen=False,
    saturation=False,
    rotate=False,
    random_crop=False,
    resize_to=None,
):
    out = Path(output_dir)
    img_dir = out / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    root = Path(project.dataset_path)

    aug = Project.from_dict(project.to_dict())
    aug.dataset_path = str(out)
    aug.images = []

    for img in project.images:
        src = root / img.relative_path
        if not src.exists() or img.broken:
            continue
        base = Image.open(src).convert("RGB")

        for c in range(copies_per_image):
            ni = deepcopy(img)
            im = base.copy()
            tags = [f"aug{c + 1}"]

            if horizontal_flip and random.random() < 0.5:
                im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                tags.append("hflip")
                for a in ni.annotations:
                    if a.bbox:
                        a.bbox = _flip_bbox_horizontal(a.bbox, img.width)
                    if a.polygon:
                        a.polygon = [[img.width - x, y] for x, y in a.polygon]

            if vertical_flip and random.random() < 0.25:
                im = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                tags.append("vflip")
                for a in ni.annotations:
                    if a.bbox:
                        a.bbox = _flip_bbox_vertical(a.bbox, img.height)
                    if a.polygon:
                        a.polygon = [[x, img.height - y] for x, y in a.polygon]

            if random_crop:
                im, ni = _random_crop_image_and_bboxes(im, ni)
                tags.append("crop")

            if rotate:
                angle = random.uniform(-8, 8)
                im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
                tags.append("rot")
                for a in ni.annotations:
                    if a.bbox:
                        a.bbox = _rotate_bbox(a.bbox, ni.width, ni.height, angle)
                _drop_segmentation_if_unsafe(ni)

            if resize_to:
                w, h = im.size
                long_side = max(w, h)
                scale = resize_to / long_side
                nw, nh = int(w * scale), int(h * scale)
                im = im.resize((nw, nh), Image.Resampling.BILINEAR)
                tags.append(f"resize{resize_to}")
                for a in ni.annotations:
                    if a.bbox:
                        a.bbox = _resize_bbox(a.bbox, scale, scale)
                    if a.polygon:
                        a.polygon = [[x * scale, y * scale] for x, y in a.polygon]
                ni.width, ni.height = nw, nh

            if brightness:
                im = ImageEnhance.Brightness(im).enhance(random.uniform(0.75, 1.25))
                tags.append("bright")
            if contrast:
                im = ImageEnhance.Contrast(im).enhance(random.uniform(0.75, 1.35))
                tags.append("contrast")
            if saturation:
                im = ImageEnhance.Color(im).enhance(random.uniform(0.65, 1.45))
                tags.append("sat")
            if grayscale and random.random() < 0.7:
                im = im.convert("L").convert("RGB")
                tags.append("gray")
            if blur and random.random() < 0.5:
                im = im.filter(ImageFilter.GaussianBlur(random.uniform(0.4, 1.2)))
                tags.append("blur")
            if sharpen and random.random() < 0.5:
                im = im.filter(ImageFilter.SHARPEN)
                tags.append("sharp")
            if noise and random.random() < 0.6:
                im = _add_noise(im)
                tags.append("noise")

            suffix = Path(img.filename).suffix or ".jpg"
            name = f"{Path(img.filename).stem}_{'_'.join(tags)}{suffix}"
            im.save(img_dir / name)
            ni.filename = name
            ni.relative_path = str(Path("images") / name)
            ni.width, ni.height = im.size
            for ann in ni.annotations:
                ann.source = ann.source if "augmented" in ann.source else ann.source + "+augmented"
                ann.touch()
            aug.images.append(ni)

    aug.augmentation_info = {
        "copies_per_image": copies_per_image,
        "horizontal_flip": horizontal_flip,
        "vertical_flip": vertical_flip,
        "brightness": brightness,
        "contrast": contrast,
        "grayscale": grayscale,
        "blur": blur,
        "noise": noise,
        "sharpen": sharpen,
        "saturation": saturation,
        "rotate": rotate,
        "random_crop": random_crop,
        "resize_to": resize_to,
        "note": "Segmentation-safe augmentation is limited; unsafe transforms may export bbox-only labels.",
    }
    save_project(aug, out / "visionforge_augmented_project.json")
    return aug

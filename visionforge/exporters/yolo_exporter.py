from pathlib import Path
import shutil
from visionforge.core.bbox_utils import xyxy_to_yolo

def export_yolo(project, output_dir, accepted_only=True, grouped=False):
    out = Path(output_dir)
    img_dir = out / "images"
    lbl_dir = out / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)
    class_names = [c["name"] for c in sorted(project.classes, key=lambda x: int(x["id"]))]
    if grouped:
        class_names = sorted(set(class_names + list(project.class_groups.keys())))
    class_to_id = {n: i for i, n in enumerate(class_names)}
    (out / "classes.txt").write_text("\n".join(class_names) + "\n", encoding="utf-8")
    root = Path(project.dataset_path)
    for img in project.images:
        src = root / img.relative_path
        if src.exists() and not img.broken:
            shutil.copy2(src, img_dir / img.filename)
        rows = []
        for ann in img.annotations:
            if accepted_only and ann.status != "accepted":
                continue
            if not ann.bbox:
                continue
            name = ann.class_name
            if grouped:
                for group, classes in project.class_groups.items():
                    if name in classes:
                        name = group
                        break
            cid = class_to_id.setdefault(name, len(class_to_id))
            vals = xyxy_to_yolo(ann.bbox, img.width, img.height)
            rows.append(f"{cid} {vals[0]:.6f} {vals[1]:.6f} {vals[2]:.6f} {vals[3]:.6f}")
        (lbl_dir / (Path(img.filename).stem + ".txt")).write_text("\n".join(rows), encoding="utf-8")
    return out

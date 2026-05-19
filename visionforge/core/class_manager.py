from pathlib import Path
from visionforge.config import DEFAULT_CLASS_COLORS

class ClassManager:
    def __init__(self, classes=None):
        self.classes = classes or []
    def add(self, name, color=None):
        name = name.strip()
        if not name:
            raise ValueError("Class name cannot be empty")
        for c in self.classes:
            if c["name"] == name:
                return int(c["id"])
        cid = len(self.classes)
        self.classes.append({"id": cid, "name": name, "color": color or DEFAULT_CLASS_COLORS[cid % len(DEFAULT_CLASS_COLORS)]})
        return cid
    def rename(self, old, new):
        for c in self.classes:
            if c["name"] == old:
                c["name"] = new.strip()
                return
        raise KeyError(old)
    def delete(self, name):
        self.classes = [c for c in self.classes if c["name"] != name]
        for i, c in enumerate(self.classes):
            c["id"] = i
    def merge(self, sources, target):
        self.add(target)
        return {s: target for s in sources}
    def import_txt(self, path):
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                self.add(line.strip())
    def export_txt(self, path):
        Path(path).write_text("\n".join(c["name"] for c in sorted(self.classes, key=lambda x: int(x["id"]))) + "\n", encoding="utf-8")
    def name_to_id(self):
        return {c["name"]: int(c["id"]) for c in self.classes}

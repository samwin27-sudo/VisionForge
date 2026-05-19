import json
from pathlib import Path
class ClassGroupManager:
    def __init__(self, groups=None): self.groups=groups or {}
    def create_group(self,g): self.groups.setdefault(g.strip(), [])
    def rename_group(self,old,new): self.groups[new]=self.groups.pop(old)
    def add_class(self,g,c): self.create_group(g); self.groups[g].append(c) if c not in self.groups[g] else None
    def remove_class(self,g,c): self.groups[g]=[x for x in self.groups.get(g,[]) if x!=c]
    def grouped_name(self,c):
        for g,items in self.groups.items():
            if c in items: return g
        return c
    def save(self,path): Path(path).write_text(json.dumps(self.groups,indent=2),encoding='utf-8')
    @classmethod
    def load(cls,path): return cls(json.loads(Path(path).read_text(encoding='utf-8')))

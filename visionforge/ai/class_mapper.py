import json
from pathlib import Path
class ClassMapper:
    def __init__(self,mapping=None): self.mapping=mapping or {}
    def map(self,name): return self.mapping.get(name,name)
    def set_mapping(self,model_class,project_class): self.mapping[model_class]=project_class
    def load(self,path): self.mapping=json.loads(Path(path).read_text(encoding='utf-8'))
    def save(self,path): Path(path).write_text(json.dumps(self.mapping,indent=2),encoding='utf-8')

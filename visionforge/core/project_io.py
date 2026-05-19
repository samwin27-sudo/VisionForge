import json
from pathlib import Path
from visionforge.config import PROJECT_FILE_NAME
from visionforge.core.annotation_store import Project

def default_project_path(dataset_path): return Path(dataset_path)/PROJECT_FILE_NAME
def save_project(project, path=None):
    out=Path(path) if path else default_project_path(project.dataset_path); out.parent.mkdir(parents=True,exist_ok=True); project.touch(); tmp=out.with_suffix(out.suffix+'.tmp'); tmp.write_text(json.dumps(project.to_dict(),indent=2),encoding='utf-8'); tmp.replace(out); return out
def load_project(path): return Project.from_dict(json.loads(Path(path).read_text(encoding='utf-8')))

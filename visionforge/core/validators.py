from pathlib import Path
from collections import Counter
from visionforge.core.dataset_loader import read_image_size

def validate_project(project):
    root=Path(project.dataset_path); duplicates=[k for k,v in Counter(i.filename for i in project.images).items() if v>1]; broken=[]; missing=[]
    for img in project.images:
        p=root/img.relative_path
        if not p.exists(): missing.append(img.relative_path); continue
        if read_image_size(p)[2]: broken.append(img.relative_path)
    warnings=[]
    if duplicates: warnings.append(f'Duplicate filenames found: {len(duplicates)}')
    if broken: warnings.append(f'Broken images found: {len(broken)}')
    if missing: warnings.append(f'Missing images found: {len(missing)}')
    return {'warnings':warnings,'duplicates':duplicates,'broken':broken,'missing':missing}

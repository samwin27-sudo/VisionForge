from pathlib import Path
from copy import deepcopy
import random, csv, shutil
from visionforge.core.annotation_store import Project
from visionforge.core.project_io import save_project

def randomize_dataset(project, output_dir, prefix='vf', seed=42):
    out=Path(output_dir); img_dir=out/'images'; img_dir.mkdir(parents=True,exist_ok=True); imgs=list(project.images); random.Random(seed).shuffle(imgs); root=Path(project.dataset_path); rp=Project.from_dict(project.to_dict()); rp.dataset_path=str(out); rp.images=[]; rows=[]
    for idx,img in enumerate(imgs,1):
        src=root/img.relative_path; name=f'{prefix}_{idx:06d}{Path(img.filename).suffix.lower()}'
        if src.exists(): shutil.copy2(src,img_dir/name)
        ni=deepcopy(img); rows.append({'old_filename':ni.filename,'new_filename':name}); ni.filename=name; ni.relative_path=str(Path('images')/name); rp.images.append(ni)
    with (out/'filename_mapping.csv').open('w',newline='',encoding='utf-8') as f: writer=csv.DictWriter(f,fieldnames=['old_filename','new_filename']); writer.writeheader(); writer.writerows(rows)
    save_project(rp,out/'visionforge_randomized_project.json'); return rp

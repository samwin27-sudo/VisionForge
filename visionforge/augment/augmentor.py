from pathlib import Path
from copy import deepcopy
from PIL import Image, ImageEnhance, ImageFilter
import random
from visionforge.augment.bbox_augment import flip_bbox_horizontal
from visionforge.core.annotation_store import Project
from visionforge.core.project_io import save_project

def augment_project(project, output_dir, copies_per_image=1, horizontal_flip=True, brightness=True, blur=False):
    out=Path(output_dir); img_dir=out/'images'; img_dir.mkdir(parents=True,exist_ok=True); root=Path(project.dataset_path); aug=Project.from_dict(project.to_dict()); aug.dataset_path=str(out); aug.images=[]
    for img in project.images:
        src=root/img.relative_path
        if not src.exists() or img.broken: continue
        base=Image.open(src).convert('RGB')
        for c in range(copies_per_image):
            ni=deepcopy(img); im=base.copy(); tags=[f'aug{c+1}']
            if horizontal_flip and c%2==0:
                im=im.transpose(Image.FLIP_LEFT_RIGHT); tags.append('hflip')
                for a in ni.annotations:
                    if a.bbox: a.bbox=flip_bbox_horizontal(a.bbox,img.width)
            if brightness: im=ImageEnhance.Brightness(im).enhance(random.uniform(.75,1.25)); tags.append('bright')
            if blur and c%3==0: im=im.filter(ImageFilter.GaussianBlur(.8)); tags.append('blur')
            name=f"{Path(img.filename).stem}_{'_'.join(tags)}{Path(img.filename).suffix}"; im.save(img_dir/name); ni.filename=name; ni.relative_path=str(Path('images')/name); aug.images.append(ni)
    aug.augmentation_info={'copies_per_image':copies_per_image,'horizontal_flip':horizontal_flip,'brightness':brightness,'blur':blur,'note':'Segmentation-safe augmentation is limited.'}; save_project(aug,out/'visionforge_augmented_project.json'); return aug

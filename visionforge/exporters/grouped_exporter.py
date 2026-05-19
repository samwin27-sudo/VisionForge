from pathlib import Path
from visionforge.core.annotation_store import Project
from visionforge.exporters.yolo_exporter import export_yolo
from visionforge.exporters.coco_exporter import export_coco

def clone_with_grouped_classes(project):
    p=Project.from_dict(project.to_dict()); groups=sorted(project.class_groups.keys()); p.classes=[{'id':i,'name':g,'color':'#00E5FF'} for i,g in enumerate(groups)]
    ids={c['name']:c['id'] for c in p.classes}
    for img in p.images:
        for ann in img.annotations:
            for g,cs in project.class_groups.items():
                if ann.class_name in cs: ann.class_name=g; ann.class_id=ids.get(g,0)
    return p
def export_grouped(project, output_dir, fmt='yolo'):
    gp=clone_with_grouped_classes(project); out=Path(output_dir)
    return export_yolo(gp,out/'grouped_yolo') if fmt=='yolo' else export_coco(gp,out/'grouped_coco.json')

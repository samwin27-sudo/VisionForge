import json
from pathlib import Path
from visionforge.core.annotation_store import Annotation
from visionforge.core.bbox_utils import coco_to_xyxy
from visionforge.core.polygon_utils import unflatten_polygon

def import_coco(project, coco_json):
    data=json.loads(Path(coco_json).read_text(encoding='utf-8')); cats={int(c['id']):c['name'] for c in data.get('categories',[])}; imgs={int(i['id']):i for i in data.get('images',[])}; name_to_id={c['name']:int(c['id']) for c in project.classes}; imported=0; missing=[]
    for a in data.get('annotations',[]):
        m=imgs.get(int(a['image_id'])); fname=m.get('file_name') if m else None; img=next((i for i in project.images if i.relative_path==fname or i.filename==Path(fname or '').name), None)
        if not img: missing.append(fname); continue
        cname=cats.get(int(a.get('category_id',0)),str(a.get('category_id',0)))
        if cname not in name_to_id: name_to_id[cname]=len(project.classes); project.classes.append({'id':name_to_id[cname],'name':cname,'color':'#00E5FF'})
        seg=a.get('segmentation'); poly=unflatten_polygon(seg[0]) if isinstance(seg,list) and seg and isinstance(seg[0],list) else None
        img.annotations.append(Annotation(annotation_type='polygon' if poly else 'bbox',bbox=coco_to_xyxy(a.get('bbox',[0,0,0,0])),polygon=poly,class_name=cname,class_id=name_to_id[cname],source='imported',status='accepted')); imported+=1
    return {'imported':imported,'missing_images':missing}

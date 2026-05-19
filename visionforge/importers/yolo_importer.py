from pathlib import Path
from visionforge.core.annotation_store import Annotation
from visionforge.core.bbox_utils import yolo_to_xyxy

def import_yolo(project, labels_dir, classes_txt):
    classes=[l.strip() for l in Path(classes_txt).read_text(encoding='utf-8').splitlines() if l.strip()]; name_to_id={c['name']:int(c['id']) for c in project.classes}; imported=0; missing=[]
    for lp in Path(labels_dir).glob('*.txt'):
        img=next((i for i in project.images if Path(i.filename).stem==lp.stem), None)
        if not img: missing.append(lp.name); continue
        for line in lp.read_text().splitlines():
            parts=line.split();
            if len(parts)<5: continue
            cname=classes[int(float(parts[0]))] if int(float(parts[0]))<len(classes) else parts[0]
            if cname not in name_to_id: name_to_id[cname]=len(project.classes); project.classes.append({'id':name_to_id[cname],'name':cname,'color':'#00E5FF'})
            img.annotations.append(Annotation(bbox=yolo_to_xyxy(float(parts[1]),float(parts[2]),float(parts[3]),float(parts[4]),img.width,img.height),class_name=cname,class_id=name_to_id[cname],source='imported',status='accepted')); imported+=1
    return {'imported':imported,'missing_images':missing}

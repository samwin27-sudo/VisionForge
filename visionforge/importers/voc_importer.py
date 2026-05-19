from pathlib import Path
import xml.etree.ElementTree as ET
from visionforge.core.annotation_store import Annotation

def import_voc(project, annotations_dir):
    name_to_id={c['name']:int(c['id']) for c in project.classes}; imported=0; missing=[]
    for xp in Path(annotations_dir).glob('*.xml'):
        r=ET.parse(xp).getroot(); fname=r.findtext('filename') or xp.stem+'.jpg'; img=next((i for i in project.images if i.filename==fname or Path(i.filename).stem==xp.stem), None)
        if not img: missing.append(fname); continue
        for obj in r.findall('object'):
            cname=obj.findtext('name') or 'object'; box=obj.find('bndbox')
            if box is None: continue
            if cname not in name_to_id: name_to_id[cname]=len(project.classes); project.classes.append({'id':name_to_id[cname],'name':cname,'color':'#00E5FF'})
            bbox=[float(box.findtext(t,0)) for t in ['xmin','ymin','xmax','ymax']]
            img.annotations.append(Annotation(bbox=bbox,class_name=cname,class_id=name_to_id[cname],source='imported',status='accepted')); imported+=1
    return {'imported':imported,'missing_images':missing}

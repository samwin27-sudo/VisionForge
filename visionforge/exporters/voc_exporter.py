from pathlib import Path
import shutil, xml.etree.ElementTree as ET
from visionforge.core.bbox_utils import clamp_bbox

def _sub(p,t,text=None):
    e=ET.SubElement(p,t); e.text=str(text) if text is not None else None; return e

def export_voc(project, output_dir, accepted_only=True):
    out=Path(output_dir); ad=out/'Annotations'; idr=out/'JPEGImages'; ad.mkdir(parents=True,exist_ok=True); idr.mkdir(parents=True,exist_ok=True); root=Path(project.dataset_path)
    for img in project.images:
        src=root/img.relative_path
        if src.exists() and not img.broken: shutil.copy2(src,idr/img.filename)
        r=ET.Element('annotation'); _sub(r,'filename',img.filename); sz=_sub(r,'size'); _sub(sz,'width',img.width); _sub(sz,'height',img.height); _sub(sz,'depth',3)
        for ann in img.annotations:
            if accepted_only and ann.status!='accepted': continue
            if not ann.bbox: continue
            x1,y1,x2,y2=[int(round(v)) for v in clamp_bbox(ann.bbox,img.width,img.height)]
            o=_sub(r,'object'); _sub(o,'name',ann.class_name); _sub(o,'pose','Unspecified'); _sub(o,'truncated',0); _sub(o,'difficult',0); b=_sub(o,'bndbox')
            for tag,val in [('xmin',x1),('ymin',y1),('xmax',x2),('ymax',y2)]: _sub(b,tag,val)
        ET.ElementTree(r).write(ad/(Path(img.filename).stem+'.xml'),encoding='utf-8',xml_declaration=True)
    return out

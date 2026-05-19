import json
from pathlib import Path
from visionforge.core.bbox_utils import xyxy_to_coco
from visionforge.core.polygon_utils import flatten_polygon, polygon_area

def export_coco(project, output_json, segmentation=False, accepted_only=True):
    out=Path(output_json); out.parent.mkdir(parents=True,exist_ok=True)
    cats=[{'id':int(c['id'])+1,'name':c['name'],'supercategory':'object'} for c in project.classes]; name_to_id={c['name']:int(c['id'])+1 for c in project.classes}
    images=[]; annotations=[]; aid=1
    for iid,img in enumerate(project.images,1):
        images.append({'id':iid,'file_name':img.relative_path,'width':img.width,'height':img.height})
        for ann in img.annotations:
            if accepted_only and ann.status!='accepted': continue
            if not ann.bbox: continue
            bb=xyxy_to_coco(ann.bbox); item={'id':aid,'image_id':iid,'category_id':name_to_id.get(ann.class_name,int(ann.class_id)+1),'bbox':bb,'area':bb[2]*bb[3],'iscrowd':0}
            if segmentation:
                seg=[]
                if ann.polygon:
                    seg=[flatten_polygon(ann.polygon)] if ann.polygon and len(ann.polygon[0])==2 else [flatten_polygon(p) for p in ann.polygon]
                    try: item['area']=polygon_area(ann.polygon)
                    except Exception: pass
                item['segmentation']=seg
            annotations.append(item); aid+=1
    out.write_text(json.dumps({'info':{'description':'VisionForge export','version':'1.0.0'},'images':images,'annotations':annotations,'categories':cats},indent=2),encoding='utf-8'); return out

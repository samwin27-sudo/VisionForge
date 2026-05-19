from pathlib import Path
import pandas as pd
from visionforge.core.bbox_utils import bbox_area

def export_csv_summary(project, output_csv, accepted_only=False):
    rows=[]
    for img in project.images:
        for ann in img.annotations:
            if accepted_only and ann.status!='accepted': continue
            x1=y1=x2=y2=None
            if ann.bbox: x1,y1,x2,y2=ann.bbox
            rows.append({'image_name':img.filename,'relative_path':img.relative_path,'class_name':ann.class_name,'x_min':x1,'y_min':y1,'x_max':x2,'y_max':y2,'width':img.width,'height':img.height,'bbox_area':bbox_area(ann.bbox) if ann.bbox else 0,'annotation_source':ann.source,'annotation_status':ann.status,'confidence':ann.confidence})
    out=Path(output_csv); out.parent.mkdir(parents=True,exist_ok=True); pd.DataFrame(rows).to_csv(out,index=False); return out

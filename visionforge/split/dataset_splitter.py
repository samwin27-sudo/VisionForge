from pathlib import Path
import random, json, shutil
from collections import Counter
import pandas as pd
from visionforge.core.annotation_store import Project
from visionforge.exporters.yolo_exporter import export_yolo

def split_project(project, output_dir, ratios=None, method='random', seed=42):
    ratios=ratios or {'train':.7,'val':.2,'test':.1}; out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); imgs=list(project.images); random.Random(seed).shuffle(imgs); n=len(imgs); nt=int(n*ratios['train']); nv=int(n*ratios['val']); buckets={'train':imgs[:nt],'val':imgs[nt:nt+nv],'test':imgs[nt+nv:]}; rows=[]; dist={}
    for split,items in buckets.items():
        p=Project.from_dict(project.to_dict()); p.images=items; export_yolo(p,out/split,accepted_only=True); c=Counter()
        for img in items:
            for a in img.annotations:
                if a.status=='accepted': c[a.class_name]+=1
            rows.append({'split':split,'image':img.relative_path,'annotation_count':len(img.annotations)})
        dist[split]=dict(c)
    pd.DataFrame(rows).to_csv(out/'split_summary.csv',index=False)
    with pd.ExcelWriter(out/'split_distribution.xlsx') as writer:
        for split,c in dist.items(): pd.DataFrame(list(c.items()),columns=['class_name','count']).to_excel(writer,sheet_name=split,index=False)
    cfg={'method':method,'ratios':ratios,'seed':seed,'distribution':dist}; (out/'split_config.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8'); return cfg

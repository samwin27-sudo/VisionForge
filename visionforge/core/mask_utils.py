from pathlib import Path
import numpy as np

def mask_to_bbox(mask):
    ys,xs=np.where(mask>0)
    return [float(xs.min()),float(ys.min()),float(xs.max()),float(ys.max())] if len(xs) else [0,0,0,0]
def mask_to_polygons(mask, epsilon_ratio=0.002):
    try:
        import cv2
    except ImportError:
        return []
    mask_u8=(mask>0).astype('uint8')*255
    contours,_=cv2.findContours(mask_u8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polys=[]
    for c in contours:
        if len(c)<3: continue
        eps=epsilon_ratio*cv2.arcLength(c, True); approx=cv2.approxPolyDP(c, eps, True)
        poly=[[float(p[0][0]), float(p[0][1])] for p in approx]
        if len(poly)>=3: polys.append(poly)
    return polys
def save_mask_png(mask,path):
    from PIL import Image
    Path(path).parent.mkdir(parents=True, exist_ok=True); Image.fromarray((mask>0).astype('uint8')*255).save(path)
def load_mask_png(path):
    from PIL import Image
    return np.array(Image.open(path).convert('L'))>0

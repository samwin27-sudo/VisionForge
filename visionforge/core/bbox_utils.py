from typing import Sequence, List, Tuple

def clamp_bbox(bbox: Sequence[float], width: int, height: int) -> List[float]:
    x1,y1,x2,y2=[float(v) for v in bbox]
    x1,x2=sorted((max(0,min(width,x1)), max(0,min(width,x2))))
    y1,y2=sorted((max(0,min(height,y1)), max(0,min(height,y2))))
    return [x1,y1,x2,y2]
def bbox_area(bbox):
    x1,y1,x2,y2=bbox; return max(0,float(x2)-float(x1))*max(0,float(y2)-float(y1))
def bbox_area_percent(bbox,width,height): return bbox_area(bbox)/float(width*height) if width and height else 0.0
def object_size_bucket(bbox,width,height):
    p=bbox_area_percent(bbox,width,height)
    return 'small' if p<0.02 else 'medium' if p<=0.15 else 'large'
def xyxy_to_yolo(bbox,width,height):
    x1,y1,x2,y2=clamp_bbox(bbox,width,height); bw=x2-x1; bh=y2-y1; return ((x1+bw/2)/width,(y1+bh/2)/height,bw/width,bh/height)
def yolo_to_xyxy(xc,yc,bw,bh,width,height):
    aw=bw*width; ah=bh*height; return clamp_bbox([xc*width-aw/2,yc*height-ah/2,xc*width+aw/2,yc*height+ah/2],width,height)
def xyxy_to_coco(bbox):
    x1,y1,x2,y2=bbox; return [float(x1),float(y1),max(0,float(x2)-float(x1)),max(0,float(y2)-float(y1))]
def coco_to_xyxy(bbox):
    x,y,w,h=bbox; return [float(x),float(y),float(x)+float(w),float(y)+float(h)]
def bbox_from_polygon(points):
    xs=[p[0] for p in points]; ys=[p[1] for p in points]; return [min(xs),min(ys),max(xs),max(ys)] if xs else [0,0,0,0]
def iou(a,b):
    ax1,ay1,ax2,ay2=a; bx1,by1,bx2,by2=b
    inter=bbox_area([max(ax1,bx1),max(ay1,by1),min(ax2,bx2),min(ay2,by2)])
    u=bbox_area(a)+bbox_area(b)-inter
    return inter/u if u>0 else 0.0

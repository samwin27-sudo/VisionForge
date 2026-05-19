def flip_bbox_horizontal(bbox, image_width):
    x1,y1,x2,y2=bbox; return [image_width-x2,y1,image_width-x1,y2]
def resize_bbox(bbox, sx, sy):
    x1,y1,x2,y2=bbox; return [x1*sx,y1*sy,x2*sx,y2*sy]

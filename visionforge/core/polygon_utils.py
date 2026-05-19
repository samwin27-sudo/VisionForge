def flatten_polygon(points):
    out=[]
    for x,y in points: out += [float(x), float(y)]
    return out
def unflatten_polygon(values): return [[float(values[i]), float(values[i+1])] for i in range(0,len(values)-1,2)]
def polygon_area(points):
    if len(points)<3: return 0.0
    return abs(sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points))))/2.0
def polygon_to_bbox(points):
    xs=[p[0] for p in points]; ys=[p[1] for p in points]; return [min(xs),min(ys),max(xs),max(ys)] if xs else [0,0,0,0]

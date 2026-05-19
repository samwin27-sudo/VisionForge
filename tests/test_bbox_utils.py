from visionforge.core.bbox_utils import xyxy_to_yolo, yolo_to_xyxy, object_size_bucket, iou

def test_yolo_roundtrip():
    bbox=[10,20,110,220]
    out=yolo_to_xyxy(*xyxy_to_yolo(bbox,200,400),200,400)
    assert all(abs(a-b)<1e-6 for a,b in zip(bbox,out))
def test_object_size_bucket():
    assert object_size_bucket([0,0,10,10],1000,1000)=='small'
    assert object_size_bucket([0,0,300,300],1000,1000)=='medium'
    assert object_size_bucket([0,0,800,800],1000,1000)=='large'
def test_iou(): assert 0<iou([0,0,10,10],[5,5,15,15])<1

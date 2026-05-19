from pathlib import Path
from PIL import Image
from visionforge.core.annotation_store import Annotation, Project, ImageRecord
from visionforge.exporters.yolo_exporter import export_yolo
from visionforge.exporters.coco_exporter import export_coco

def make_project(tmp_path: Path):
    Image.new('RGB',(100,100)).save(tmp_path/'a.jpg')
    return Project(dataset_path=str(tmp_path),classes=[{'id':0,'name':'car','color':'#fff'}],images=[ImageRecord(filename='a.jpg',relative_path='a.jpg',width=100,height=100,annotations=[Annotation(bbox=[10,10,50,50],class_name='car',class_id=0)])])
def test_yolo_export(tmp_path):
    out=export_yolo(make_project(tmp_path), tmp_path/'out')
    assert (out/'labels'/'a.txt').exists()
def test_coco_export(tmp_path):
    out=export_coco(make_project(tmp_path), tmp_path/'coco.json')
    assert out.exists()

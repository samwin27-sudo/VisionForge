from visionforge.core.annotation_store import Annotation, AnnotationStore, ImageRecord

def test_add_class_and_annotation():
    s=AnnotationStore(); s.set_dataset('/tmp',[ImageRecord(filename='a.jpg',relative_path='a.jpg',width=100,height=100)])
    cid=s.add_class('car'); ann=s.add_annotation(0, Annotation(bbox=[1,2,3,4],class_name='car',class_id=cid))
    assert s.images[0].annotations[0].annotation_id==ann.annotation_id
    assert s.accepted_annotations(s.images[0])[0].class_name=='car'

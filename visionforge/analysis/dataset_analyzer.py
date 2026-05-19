from collections import Counter
from visionforge.core.bbox_utils import object_size_bucket
from visionforge.core.validators import validate_project

def analyze_project(project):
    total_images=len(project.images); annotated=sum(1 for i in project.images if any(a.status=='accepted' for a in i.annotations)); total=sum(len(i.annotations) for i in project.images)
    bboxes=sum(1 for i in project.images for a in i.annotations if a.bbox); masks=sum(1 for i in project.images for a in i.annotations if a.mask_path or a.polygon)
    class_obj=Counter(); class_img=Counter(); src=Counter(); status=Counter(); size=Counter(); det_only=0; seg_count=0
    for img in project.images:
        seen=set()
        for a in img.annotations:
            class_obj[a.class_name]+=1; seen.add(a.class_name); src[a.source]+=1; status[a.status]+=1
            if a.bbox: size[object_size_bucket(a.bbox,img.width,img.height)]+=1
            if a.polygon or a.mask_path or a.annotation_type in {'polygon','mask'}: seg_count+=1
            elif a.bbox: det_only+=1
        for c in seen: class_img[c]+=1
    counts=list(class_obj.values()); avg=sum(counts)/len(counts) if counts else 0; imbalance=(max(counts)/min(counts)) if counts and min(counts)>0 else 0
    v=validate_project(project)
    return {'total_images':total_images,'total_annotated_images':annotated,'total_unannotated_images':total_images-annotated,'total_annotations':total,'total_bounding_boxes':bboxes,'total_segmentation_masks':masks,'class_wise_object_count':dict(class_obj),'class_wise_image_count':dict(class_img),'average_boxes_per_image':bboxes/total_images if total_images else 0,'images_with_no_labels':[i.relative_path for i in project.images if not i.annotations],'images_with_too_many_labels':[i.relative_path for i in project.images if len(i.annotations)>50],'missing_label_files':[],'broken_image_files':v['broken'],'missing_image_files':v['missing'],'duplicate_filenames':v['duplicates'],'annotation_source_counts':dict(src),'annotation_status_counts':dict(status),'object_size_distribution':{'small':size.get('small',0),'medium':size.get('medium',0),'large':size.get('large',0)},'class_imbalance_ratio':imbalance,'underrepresented_classes':[c for c,n in class_obj.items() if avg and n<avg*0.5],'overrepresented_classes':[c for c,n in class_obj.items() if avg and n>avg*1.5],'dataset_class_coverage_percent':{k:(v/total*100 if total else 0) for k,v in class_obj.items()},'segmentation_coverage_percentage':seg_count/total*100 if total else 0,'detection_only_count':det_only,'segmentation_annotation_count':seg_count,'split_distribution':project.split_info,'warnings':v['warnings']}

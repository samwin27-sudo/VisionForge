def calculate_readiness_score(analysis, segmentation_mode_used=False):
    total=analysis.get('total_images',0) or 0; annotated=analysis.get('total_annotated_images',0) or 0; ann=analysis.get('total_annotations',0) or 0
    warnings=list(analysis.get('warnings',[])); rec=[]; status=analysis.get('annotation_status_counts',{}); sizes=analysis.get('object_size_distribution',{})
    coverage=(annotated/total if total else 0)*20
    imbalance=analysis.get('class_imbalance_ratio',0) or 0; balance=15 if imbalance and imbalance<=2 else 10 if imbalance<=5 else 5 if imbalance<=10 else 2
    diversity=sum(1 for k in ['small','medium','large'] if sizes.get(k,0)>0)/3*10
    small=min((sizes.get('small',0)/max(ann,1))/0.2,1)*10
    health=10 if not analysis.get('broken_image_files') and not analysis.get('missing_image_files') else 5
    pending=status.get('pending',0); accepted=status.get('accepted',0); review=(accepted/max(accepted+pending,1))*10
    split=10 if analysis.get('split_distribution') else 3; scale=min(ann/10000,1)*10
    seg=5
    if segmentation_mode_used: seg=min((analysis.get('segmentation_coverage_percentage',0) or 0)/50,1)*5
    if pending: warnings.append(f'{pending} annotations are still pending AI review.'); rec.append('Review pending AI labels before training.')
    if imbalance>5: warnings.append(f'Class imbalance ratio is high: {imbalance:.2f}'); rec.append('Oversample underrepresented classes or collect more data.')
    if small<5: warnings.append('Small object coverage is weak.'); rec.append('Add more far-distance/small-object samples.')
    if not analysis.get('split_distribution'): rec.append('Create a train/val/test split before training.')
    if ann<1000: warnings.append('Dataset scale is still small for robust training.'); rec.append('Collect more samples across lighting, distance, weather, and object sizes.')
    if analysis.get('underrepresented_classes'): rec.append('Add samples for underrepresented classes: '+', '.join(analysis['underrepresented_classes']))
    score=int(round(max(0,min(100,coverage+balance+diversity+small+health+review+split+scale+seg))))
    return {'score':score,'risk_level':'Low Risk' if score>=80 else 'Medium Risk' if score>=55 else 'High Risk','warnings':warnings,'recommendations':sorted(set(rec))}

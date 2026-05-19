from visionforge.analysis.readiness_score import calculate_readiness_score

def test_readiness_score_shape():
    analysis={'total_images':10,'total_annotated_images':8,'total_annotations':100,'class_imbalance_ratio':2,'annotation_status_counts':{'accepted':90,'pending':10},'object_size_distribution':{'small':20,'medium':60,'large':20},'broken_image_files':[],'missing_image_files':[],'split_distribution':{'train':{},'val':{},'test':{}},'warnings':[]}
    r=calculate_readiness_score(analysis)
    assert 0<=r['score']<=100
    assert r['risk_level'] in {'Low Risk','Medium Risk','High Risk'}

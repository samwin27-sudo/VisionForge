VALID_STATUSES={'pending','accepted','rejected','edited'}
def set_status(annotation, status):
    if status not in VALID_STATUSES: raise ValueError(status)
    annotation.status=status; annotation.touch()
def accept_all(image, min_confidence=None):
    n=0
    for a in image.annotations:
        if a.status=='pending' and (min_confidence is None or (a.confidence or 0)>=min_confidence): set_status(a,'accepted'); n+=1
    return n
def reject_all(image):
    n=0
    for a in image.annotations:
        if a.status=='pending': set_status(a,'rejected'); n+=1
    return n
def review_counts(project):
    d={s:0 for s in VALID_STATUSES}
    for i in project.images:
        for a in i.annotations: d[a.status]=d.get(a.status,0)+1
    return d

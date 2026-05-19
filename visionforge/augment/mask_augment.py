import numpy as np
def flip_mask_horizontal(mask): return np.fliplr(mask)
def segmentation_safe_warning(): return 'Segmentation-safe augmentation is limited. Masks must be transformed with the same geometric operation as images.'

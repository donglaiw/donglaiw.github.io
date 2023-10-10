import torch
import random
import numpy as np

from scipy.ndimage import distance_transform_edt
from skimage.morphology import skeletonize, skeletonize_3d, medial_axis
from skimage.morphology import dilation, remove_small_holes
from skimage.filters import gaussian


class SDT(object):
    """Generator for skeleton-based distance transform, Euclidean distance transform
    and skeleton with associated radius for instance segmentation.
    """
    resolution = (1.0, 1.0)
    skel_func_dict = {
        1: skeletonize,
        2: skeletonize_3d,
        3: medial_axis,
    }
    eps = 1e-6
    
    def __init__(self, mode='sdt', alpha=1.0, skel_func=1, smooth=False, smooth_sigma=2.0,
                 smooth_threshold=0.5, smooth_skeleton_only=False, semantic_thres=0, 
                 background_value=-1.0, quantization=False, quantization_levels=10, 
                 pre_computed=False):
        assert mode in ['sdt', 'edt', 'sr']
        self.mode = mode

        self.alpha = alpha
        self.smooth = smooth
        self.smooth_sigma = smooth_sigma
        self.smooth_threshold = smooth_threshold
        self.smooth_skeleton_only = smooth_skeleton_only

        self.semantic_thres = semantic_thres

        self.quantization = False if mode=='sr' else quantization
        self.quantization_levels = quantization_levels

        assert -1.0 <= background_value <= 0.0
        self.background_value = background_value

        self.skel_func = skel_func
        self.pre_computed = pre_computed

    def __call__(self, sample):
        if self.pre_computed: 
            return self.process_pre_computed(sample)

        label = sample['label']
        if self.mode == 'sdt':
            distance, skeleton, semantic, label = self.skeleton_transform(label)
        elif self.mode == 'edt':
            distance, skeleton, semantic, label = self.distance_transform(label)
        else:
            distance, skeleton, semantic, label = self.skeleton_and_radius(label)

        # quantization
        if self.quantization:
            distance_orig = distance.copy()
            sample["distance_orig"] = distance_orig
            distance = energy_quantize(distance, 
                levels=self.quantization_levels)

        sample["label"] = label # updated label (might be smoothed)
        sample["distance"] = distance
        sample["skeleton"] = skeleton
        semantic = (semantic > self.semantic_thres).astype(np.float32)
        sample["semantic"] = semantic
        return sample

    def smooth_edge(self, binary):
        """Smooth the object contour.
        """
        for _ in range(2):
            binary = gaussian(binary, sigma=self.smooth_sigma, preserve_range=True)
            binary = (binary > self.smooth_threshold).astype(np.uint8)

        return binary

    def skeleton_transform(self, label):
        """Skeleton-based distance transform (SDT).
        """
        label_shape = label.shape[1:]

        skeleton = np.zeros(label_shape, dtype=np.uint8)
        distance = np.zeros(label_shape, dtype=np.float32)
        semantic = np.zeros(label_shape, dtype=np.uint8)

        for idx in range(label.shape[0]):
            temp1 = label[idx].astype(bool)
            temp2 = remove_small_holes(temp1, 16, connectivity=1)
            binary = temp2.copy()

            if self.smooth:
                binary = self.smooth_edge(binary)
                if binary.astype(int).sum() <= 32:
                    # Reverse the smoothing operation if it makes
                    # the output mask empty (or very small).
                    binary = temp2.copy()
                else:
                    if self.smooth_skeleton_only:
                        binary = binary*temp2
                    else:
                        temp2 = binary.copy()

            label[idx] = temp2
            semantic += temp2
            skeleton_mask = self.skel_func_dict[self.skel_func](binary)
            skeleton_mask = (skeleton_mask!=0).astype(np.uint8)
            skeleton += skeleton_mask
            
            skeleton_edt = distance_transform_edt(1-skeleton_mask, self.resolution)
            boundary_edt = distance_transform_edt(temp2, self.resolution)
            energy = boundary_edt / (skeleton_edt + boundary_edt + self.eps) # normalize
            energy = energy**self.alpha
            
            distance = np.maximum(distance, energy*temp2)

        # generate boundary 
        distance[np.where(semantic==0)]=self.background_value
        skeleton = dilation(skeleton, np.ones((5,5), dtype=np.uint8))

        return distance, skeleton, semantic, label

    def distance_transform(self, label):
        """Euclidean distance transform (DT or EDT).
        """
        label_shape = label.shape[1:]

        distance = np.zeros(label_shape, dtype=np.float32)
        semantic = np.zeros(label_shape, dtype=np.uint8)
        _placebo = np.zeros(label_shape, dtype=np.uint8)

        for idx in range(label.shape[0]):
            temp1 = label[idx].astype(bool)
            temp2 = remove_small_holes(temp1, 16, connectivity=1)
            binary = temp2.copy()

            if self.smooth:
                binary = self.smooth_edge(binary)
                if binary.astype(int).sum() <= 32:
                    binary = temp2.copy()
                else:
                    temp2 = binary.copy()

            label[idx] = temp2
            semantic += temp2
            boundary_edt = distance_transform_edt(temp2, self.resolution)
            energy = boundary_edt / (boundary_edt.max() + self.eps) # normalize
            distance = np.maximum(distance, energy*temp2)

        # generate boundary 
        distance[np.where(semantic==0)]=self.background_value
        return distance, _placebo, semantic, label

    def skeleton_and_radius(self, label):
        """Generate object skeleton with associated radius.
        """
        label_shape = label.shape[1:]

        skeleton = np.zeros(label_shape, dtype=np.uint8)
        distance = np.zeros(label_shape, dtype=np.float32)
        semantic = np.zeros(label_shape, dtype=np.uint8)

        for idx in range(label.shape[0]):
            temp1 = label[idx].astype(bool)
            temp2 = remove_small_holes(temp1, 16, connectivity=1)
            binary = temp2.copy()

            if self.smooth:
                binary = self.smooth_edge(binary)
                if binary.astype(int).sum() <= 32:
                    binary = temp2.copy()
                else:
                    temp2 = binary.copy()
                
            label[idx] = temp2
            semantic += temp2
            skeleton_mask = self.skel_func_dict[self.skel_func](binary)
            skeleton_mask = (skeleton_mask!=0).astype(np.uint8)
            skeleton_mask = dilation(skeleton_mask, np.ones((3,3), dtype=np.uint8))
            skeleton += skeleton_mask
            boundary_edt = distance_transform_edt(temp2, self.resolution)
                
            distance = np.maximum(distance, boundary_edt*skeleton_mask)

        semantic = skeleton
        return distance, skeleton, semantic, label

    def process_pre_computed(self, sample):
        """Process pre-computed energy maps.
        """
        distance = sample['pre_computed'].astype(np.float32)
        distance = distance / 255.0
        distance = distance * (1-self.background_value) + self.background_value

        sample["skeleton"] = (distance > 0.95).astype(np.uint8)
        sample["semantic"] = (distance > 0.0 ).astype(np.uint8)
        
        # quantization
        if self.quantization:
            distance_orig = distance.copy()
            sample["distance_orig"] = distance_orig
            distance = energy_quantize(distance, 
                levels=self.quantization_levels)

        sample["distance"] = distance
        return sample

import SimpleITK as sitk
import numpy as np
import logging

logger = logging.getLogger(__name__)

from custom_algorithm import Hanseg2023Algorithm


class MyHanseg2023Algorithm(Hanseg2023Algorithm):
    def __init__(self):
        super().__init__()

    def predict(self, *, image_ct: sitk.Image, image_mrt1: sitk.Image) -> sitk.Image:
        
        # dummy example that produces an empty segmentation
        pred_seg = image_ct * 0
        pred_seg = sitk.Cast(pred_seg, sitk.sitkUInt8)
        
        # output should be a sitk image with the same size, spacing, origin and direction as the original input image_ct
        return pred_seg


if __name__ == "__main__":
    MyHanseg2023Algorithm().process()

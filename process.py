import SimpleITK as sitk
import numpy as np
import logging

logger = logging.getLogger(__name__)

from custom_algorithm import Hanseg2023Algorithm

LABEL_dict = {
    "background": 0,
    "A_Carotid_L": 1,
    "A_Carotid_R": 2,
    "Arytenoid": 3,
    "Bone_Mandible": 4,
    "Brainstem": 5,
    "BuccalMucosa": 6,
    "Cavity_Oral": 7,
    "Cochlea_L": 8,
    "Cochlea_R": 9,
    "Cricopharyngeus": 10,
    "Esophagus_S": 11,
    "Eye_AL": 12,
    "Eye_AR": 13,
    "Eye_PL": 14,
    "Eye_PR": 15,
    "Glnd_Lacrimal_L": 16,
    "Glnd_Lacrimal_R": 17,
    "Glnd_Submand_L": 18,
    "Glnd_Submand_R": 19,
    "Glnd_Thyroid": 20,
    "Glottis": 21,
    "Larynx_SG": 22,
    "Lips": 23,
    "OpticChiasm": 24,
    "OpticNrv_L": 25,
    "OpticNrv_R": 26,
    "Parotid_L": 27,
    "Parotid_R": 28,
    "Pituitary": 29,
    "SpinalCord": 30,
}

class MyHanseg2023Algorithm(Hanseg2023Algorithm):
    def __init__(self):
        super().__init__()

    def predict(self, *, image_ct: sitk.Image, image_mrt1: sitk.Image) -> sitk.Image:
        
        # create an empty segmentation same size as ct image
        output_seg = image_ct * 0
        # inpaint a simple cuboid shape in the 3D segmentation mask
        ct_shape = image_ct.GetSize()
        output_seg[int(ct_shape[0]*0.1):int(ct_shape[0]*0.6), 
                   int(ct_shape[1]*0.2):int(ct_shape[1]*0.7), 
                   int(ct_shape[2]*0.3):int(ct_shape[2]*0.8)] = 1
        
        # output should be a sitk image with the same size, spacing, origin and direction as the original input image_ct
        output_seg = sitk.Cast(output_seg, sitk.sitkUInt8)
        return output_seg


if __name__ == "__main__":
    MyHanseg2023Algorithm().process()
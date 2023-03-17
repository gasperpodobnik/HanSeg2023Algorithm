import SimpleITK
import numpy as np
import logging

logger = logging.getLogger(__name__)

from custom_algorithm import Hanseg2023algorithm


class MyHanseg2023algorithm(Hanseg2023algorithm):
    def __init__(self):
        super().__init__()

    def predict(
        self, *, image_ct: SimpleITK.Image, image_mrt1: SimpleITK.Image
    ) -> SimpleITK.Image:
        # Segment all values greater than 2 in the input image
        return SimpleITK.BinaryThreshold(
            image1=image_ct,
            lowerThreshold=100,
            upperThreshold=700,
            insideValue=1,
            outsideValue=0,
        )


if __name__ == "__main__":
    MyHanseg2023algorithm().process()

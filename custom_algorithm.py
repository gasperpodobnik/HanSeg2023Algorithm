import SimpleITK as sitk

from evalutils import SegmentationAlgorithm

import logging
from pathlib import Path
from typing import (
    Optional,
    Pattern,
    Tuple,
)

from pandas import DataFrame
from evalutils.exceptions import FileLoaderError, ValidationError
from evalutils.validators import DataFrameValidator
from evalutils.io import (
    ImageLoader,
)

logger = logging.getLogger(__name__)


class HanSegUniquePathIndicesValidator(DataFrameValidator):
    """
    Validates that the indicies from the filenames are unique
    """

    def validate(self, *, df: DataFrame):
        try:
            paths_ct = df["path_ct"].tolist()
            paths_mrt1 = df["path_mrt1"].tolist()
            paths = paths_ct + paths_mrt1
        except KeyError:
            raise ValidationError(
                "Column `path_ct` or `path_mrt1` not found in DataFrame."
            )

        assert len(paths_ct) == len(
            paths_mrt1
        ), "The number of CT and MR images is not equal."


class HanSegUniqueImagesValidator(DataFrameValidator):
    """
    Validates that each image in the set is unique
    """

    def validate(self, *, df: DataFrame):
        try:
            hashes_ct = df["hash_ct"].tolist()
            hashes_mrt1 = df["hash_mrt1"].tolist()
            hashes = hashes_ct + hashes_mrt1
        except KeyError:
            raise ValidationError(
                "Column `hash_ct` or `hash_mrt1` not found in DataFrame."
            )

        if len(set(hashes)) != len(hashes):
            raise ValidationError(
                "The images are not unique, please submit a unique image for "
                "each case."
            )


class Hanseg2023Algorithm(SegmentationAlgorithm):
    def __init__(
        self,
        input_path=Path("/input/images/"),
        output_path=Path("/output/images/head_neck_oar/"),
        **kwargs,
    ):
        super().__init__(
            validators=dict(
                input_image=(
                    HanSegUniqueImagesValidator(),
                    HanSegUniquePathIndicesValidator(),
                )
            ),
            input_path=input_path,
            output_path=output_path,
            **kwargs,
        )

    def _load_input_image(self, *, case) -> Tuple[sitk.Image, Path]:
        input_image_file_path_ct = case["path_ct"]
        input_image_file_path_mrt1 = case["path_mrt1"]

        input_image_file_loader = self._file_loaders["input_image"]
        if not isinstance(input_image_file_loader, ImageLoader):
            raise RuntimeError("The used FileLoader was not of subclass ImageLoader")

        # Load the image for this case
        input_image_ct = input_image_file_loader.load_image(input_image_file_path_ct)
        input_image_mrt1 = input_image_file_loader.load_image(
            input_image_file_path_mrt1
        )

        # Check that it is the expected image
        if input_image_file_loader.hash_image(input_image_ct) != case["hash_ct"]:
            raise RuntimeError("CT image hashes do not match")
        if input_image_file_loader.hash_image(input_image_mrt1) != case["hash_mrt1"]:
            raise RuntimeError("MR image hashes do not match")

        return (
            input_image_ct,
            input_image_file_path_ct,
            input_image_mrt1,
            input_image_file_path_mrt1,
        )

    def process_case(self, *, idx, case):
        # Load and test the image for this case
        (
            input_image_ct,
            input_image_file_path_ct,
            input_image_mrt1,
            input_image_file_path_mrt1,
        ) = self._load_input_image(case=case)

        # Segment nodule candidates
        segmented_nodules = self.predict(
            image_ct=input_image_ct, image_mrt1=input_image_mrt1
        )

        # Write resulting segmentation to output location
        segmentation_path = self._output_path / input_image_file_path_ct.name.replace(
            "_CT", "_seg"
        )
        self._output_path.mkdir(parents=True, exist_ok=True)
        sitk.WriteImage(segmented_nodules, str(segmentation_path), True)

        # Write segmentation file path to result.json for this case
        return {
            "outputs": [dict(type="metaio_image", filename=segmentation_path.name)],
            "inputs": [
                dict(type="metaio_ct_image", filename=input_image_file_path_ct.name),
                dict(
                    type="metaio_mrt1_image", filename=input_image_file_path_mrt1.name
                ),
            ],
            "error_messages": [],
        }

    def _load_cases(
        self,
        *,
        folder: Path,
        file_loader: ImageLoader,
        file_filter: Optional[Pattern[str]] = None,
    ) -> DataFrame:
        cases = []

        paths_ct = sorted(folder.glob("ct/*"), key=self._file_sorter_key)
        paths_mrt1 = sorted(folder.glob("t1-mri/*"), key=self._file_sorter_key)

        for pth_ct, pth_mr in zip(paths_ct, paths_mrt1):
            if file_filter is None or (
                file_filter.match(str(pth_ct)) and file_filter.match(str(pth_mr))
            ):
                try:
                    case_ct = file_loader.load(fname=pth_ct)[0]
                    case_mrt1 = file_loader.load(fname=pth_mr)[0]
                    new_cases = [
                        {
                            "hash_ct": case_ct["hash"],
                            "path_ct": case_ct["path"],
                            "hash_mrt1": case_mrt1["hash"],
                            "path_mrt1": case_mrt1["path"],
                        }
                    ]
                except FileLoaderError:
                    logger.warning(
                        f"Could not load {pth_ct.name} or {pth_mr.name} using {file_loader}."
                    )
                else:
                    cases += new_cases
            else:
                logger.info(
                    f"Skip loading {pth_ct.name} and {pth_mr.name} because it doesn't match {file_filter}."
                )

        if len(cases) == 0:
            raise FileLoaderError(
                f"Could not load any files in {folder} with " f"{file_loader}."
            )

        return DataFrame(cases)

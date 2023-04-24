# An example algorithm docker image for HaN-Seg 2023 challenge.

Author: G. Podobnik*\
*Credits to the authors of the [MIDOG challenge reference docker documentation](https://github.com/DeepPathology/MIDOG_reference_docker) on which this is based.

This docker image serves as a template for preparing an algorithm docker image for the **[HaN-Seg 2023 challenge](https://han-seg2023.grand-challenge.org/)**. It packs some scripts and path definitions that are necessary to run your algorithm on the grand-challenge.org platform, so you do not have to bother with that.\
To better understand the bigger picture, you may want to read the blog post of grand-challenge.org on [how to create an algorithm](https://grand-challenge.org/blogs/create-an-algorithm/).

<sub>(The authors of the MIDOG challenge kindly provided a introduction to docker containers and how to prepare an algorithm docker image. Here is the link to their video: https://www.youtube.com/watch?v=Zkhrwark3bg)</sub>

## Content:
1. [Prerequisites](#prerequisites)
2. [An overview of the structure of this example](#overview)
3. [Packing your algorithm into a docker container image](#todocker)
4. [Building your container](#build)
5. [Testing your container](#test)
6. [Generating the bundle for uploading your algorithm](#export)

## 1. Prerequisites <a name="prerequisites"></a>

[Recommendation for windows users](https://grand-challenge.org/documentation/setting-up-wsl-with-gpu-support-for-windows-11/):
>Windows tip: It is highly recommended to install [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) to work with Docker on a Linux environment within Windows. Please make sure to install WSL 2 by following the instructions on the same page. In this tutorial, we have used WSL 2 with Ubuntu 18.04 LTS. Also, note that the basic version of WSL 2 does not come with GPU support. Please [watch the official tutorial by Microsoft on installing WSL 2 with GPU support](https://www.youtube.com/watch?v=PdxXlZJiuxA). The alternative is to work purely out of Ubuntu, or any other flavor of Linux.


**Please follow the following steps:**
- The container is based on docker, so you need to [install docker first](https://www.docker.com/get-started).
- Optional (but strongly recommended): If you want to have GPU support for local testing, you want to install the [NVIDIA container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

- You then need to clone this repository:
```
git clone https://github.com/gasperpodobnik/HanSeg2023Algorithm.git
```

- You will also need evalutils (provided by grand-challenge):
```
pip install evalutils
```



## 2. An overview of the structure of this example <a name="overview"></a>

This a dummy example that produces on empty segmentation mask. The main files are:
- [custom_algorithm.py](custom_algorithm.py): It provides the `Hanseg2023Algorithm` class that inherits from evalutils' `SegmentationAlgorithm` class and configures input and output paths so that CT & MR image pairs are correctly loaded and that output segmentation mask is saved to the expected location. We advise you to leave this file as it is and only change the [process.py](process.py) script that is described below. 

- [process.py](process.py): This is the main file that is executed by the container and the best location to implement your algorithm. It includes the `predict()` method that provides the CT image (`image_ct`) and MR image (`image_mrt1`), both are in type `SimpleITK.Image`. \
This method should return segmentation (`output_seg`) in form of `SimpleITK.Image` that should have the same *origin*, *spacing*, *size* and *direction* as the `image_ct` (this is because all ground truth segmentations were prepared in the CT image domain). Saving of `output_seg` is already handled by the the parent classes, so you do not have to worry about that. This script also includes `LABEL_dict`, a dictionary, that can be used to process output segmentation labels (if your algorithm does not already return expected `organ name - label` pairs).\
We advise you to load and instanciate your model in the `__init__()` method of the `MyHanseg2023Algorithm` class. This way, the model will be loaded only once when the container is started and not for each image. You can then use the `predict()` method to process each image independently.\
**NOTE 1**: `image_ct` and `image_mrt1` are not preprocessed to same spacing/size/origin, nor are they registered, so this is something that you might want to do before feeding them to your model (of course this depends what your method requires). To avoid unwanted registration errors, you should note that most MR images have smaller field of view than CT image, however, we require a segmentation of the same size as CT image (similarly to the clinical practice).\
**NOTE 2**: `output_seg` should only include integer labels between 0-30 (no floating point values) and should be casted to `SimpleITK.sitkUInt8` precision before returning it. 

## 3. Embedding your algorithm into an algorithm docker container <a name="todocker"></a>

You can also add additional functions/methods to the `MyHanseg2023Algorithm` class (such as a function to register CT and MR image), include additional scripts and import additional python libraries. When adding additional scripts, make sure to add them to the `COPY` command in the [Dockerfile](Dockerfile) so that they will be included in the container. All the required python packages should be listed in the [requirements.txt](requirements.txt) file so that they are installed when the container is built on the grand-challenges server.
Model weights and other files should also copied to the container using the `COPY` command (same as for additional scripts), see [Dockerfile](Dockerfile#L26) (line 26).

Most likely you will need a different base image to build your container (e.g. Tensorflow or Pytorch). This can be achieved by changing the `FROM` command in the [Dockerfile](Dockerfile), e.g. `FROM nvcr.io/nvidia/pytorch:22.12-py3` for Pytorch.\


## 4. Building your container <a name="build"></a>

To test if all dependencies are met, you should run the file `build.bat` (Windows) / `build.sh` (Linux) to build the docker container. Please note that the next step (testing the container) also runs a build, so this step is not mandatory if you are certain that everything is set up correctly.

## 5. Testing your container <a name="test"></a>

Before you run and tests, you should copy a few test images (or at least one) to the project `test` directory. The test images can be in the same format as the images provided in our Zenodo dataset and need to be organized as follows:
```
project
│   README.md
│   ...
└───test
    └───images
        └───ct
        │       e.g. case_01_IMG_CT.nrrd
        │       ...
        │       
        └───t1-mri
        │       e.g. case_01_IMG_MR_T1.nrrd
        │       ...
```
After you prepare the `test` directory and before you make any modifications the `process.py` script, you can run the `test.bat` (Windows) or `test.sh` (Linux) script to test if you successfully installed everything and copied all the required files to the `test` directory. If the test is successful, there should be a couple of dummy segmentation files in the `output/images/head_neck_oar` directory that are automatically created by the test script.

You can then proceed to modify the `process.py` script to implement your algorithm (do not forget to also modify the [Dockerfile](Dockerfile#L1) `FROM` command and [set the path to your model weights](Dockerfile#L26)). To test your container, you should run `test.bat` (on Windows) or `test.sh` (on Linux, might require sudo priviledges). This will run the test image(s) provided in the test folder through your model and save predicted segmentation masks to the `output/images/head_neck_oar` directory. You can then compare these segmentation masks with the ones that you expected to receive from the model. If they match, that's a good sign that your algorithm is working correctly. If not, you should check the `process.py` script and make sure that inference code is correct.
## 6. Generating the bundle for uploading your algorithm <a name="export"></a>

Finally, you need to run the `export.sh` (Linux) or `export.bat` script to package your docker image. This step creates a file with the extension ".tar.gz", which you can then upload to grand-challenge to submit your algorithm.

## 7. Creating an "Algorithm" on GrandChallenge and submitting your solution to the HaN-Seg 2023 Challenge

**Note: Submission to grand-challenge.org will open on March 23th.**

- Before submitting to the challenge, you should first test your docker container locally. You can do this by modifiying [test.sh](test.sh) bash script. [This](https://grand-challenge.org/documentation/building-and-testing-the-container/) might help you with testing.
- In order to submit your docker container, you first have to add an **Algorithm** entry for your docker container [here](https://han-seg2023.grand-challenge.org/evaluation/preliminary-test-phase/submissions/create/).
- After saving, you can add your docker container (or you can also [overwrite your container](https://grand-challenge.org/documentation/exporting-the-container/)). Overwriting the container is recommended when submitting a new iteration of same method (e.g. when you fix potential bugs).
- Please note that it can take a while (several minutes) until the container becomes active (you can refresh the page to see the status).
- You can also try out your algorithm. You can use on of the train images to test if predictions are as expected.
- Finally, you can submit your docker container to HaN-Seg 2023 Challenge by clicking on the "Save" button

## General remarks
- The training is not done as part of the docker container, so please make sure that you only run inference within the container.
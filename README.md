# An example algorithm docker image for HaN-Seg 2023 challenge.

Author: G. Podobnik*\
*Credits to the authors of the [MIDOG challenge reference docker documentation](https://github.com/DeepPathology/MIDOG_reference_docker) on which this is based.

This docker image serves as a template for preparing an algorithm docker image for the **[HaN-Seg 2023 challenge](https://han-seg2023.grand-challenge.org/)**. It packs some scripts and path definitions that are necessary to run your algorithm on the grand-challenge.org platform, so you do not have to worry about that.

You will have to provide all files to run your model in a docker container. This example may be of help for this. We also provide a quick explanation of how the container works [here](https://www.youtube.com/watch?v=Zkhrwark3bg).

For reference, you may also want to read the blog post of grand-challenge.org on [how to create an algorithm](https://grand-challenge.org/blogs/create-an-algorithm/).

## Content:
1. [Prerequisites](#prerequisites)
2. [An overview of the structure of this example](#overview)
3. [Packing your algorithm into a docker container image](#todocker)
4. [Building your container](#build)
5. [Testing your container](#test)
6. [Generating the bundle for uploading your algorithm](#export)

## 1. Prerequisites <a name="prerequisites"></a>

The container is based on docker, so you need to [install docker first](https://www.docker.com/get-started). 

Second, you need to clone this repository:
```
git clone https://github.com/gasperpodobnik/HanSeg2023Algorithm.git
```

You will also need evalutils (provided by grand-challenge):
```
pip install evalutils
```

Optional (and strongly recommended): If you want to have GPU support for local testing, you want to install the [NVIDIA container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

As stated by the grand-challenge team:
>Windows tip: It is highly recommended to install [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) to work with Docker on a Linux environment within Windows. Please make sure to install WSL 2 by following the instructions on the same page. In this tutorial, we have used WSL 2 with Ubuntu 18.04 LTS. Also, note that the basic version of WSL 2 does not come with GPU support. Please [watch the official tutorial by Microsoft on installing WSL 2 with GPU support](https://www.youtube.com/watch?v=PdxXlZJiuxA). The alternative is to work purely out of Ubuntu, or any other flavor of Linux.

## 2. An overview of the structure of this example <a name="overview"></a>

This a dummy example that produces on empty segmentation mask. The main files are:
- [custom_algorithm.py](custom_algorithm.py): It provides the `Hanseg2023Algorithm` class that inherits from evalutils' `SegmentationAlgorithm` class and configures input and output paths so that CT & MR image pairs are correctly loaded and that output segmentation mask is saved to the right location. We advise you to leave this file as it is and only change the [process.py](process.py) script that is described below. 

- [process.py](process.py): This is the main file that is executed by the container and the best location to implement inference of your algorithm. It includes the `predict()` method that provides the the CT image (`image_ct`) and MR image (`image_mrt1`), both are given in `SimpleITK.Image` format. \
This method should return segmentation (`output_seg`) in form of `SimpleITK.Image` that should have the same *origin*, *spacing*, *size* and *direction* as the `image_ct` (this is because all ground truth segmentations were prepared in the CT image domain). Saving of `output_seg` is already handled by the the `Hanseg2023Algorithm` class, so you do not have to worry about that. This script also includes `LABEL_dict` dictionary that can be used to adjust output segmentation labels (if your algorithm does not already return expected labels).\
**Note**: `output_seg` should only include integer labels between 0-30 (no floating point values) and should be casted to `sitk.sitkUInt8` before returning it. 

## 3. Embedding your algorithm into an algorithm docker container <a name="todocker"></a>

We advise you to load and instanciate your model in the `__init__()` method of the `Hanseg2023Algorithm` class. This way, the model will be loaded only once when the container is started and not for each image. You can then use the `predict()` method to then process each image independently. You can, of course, also add additional methods to the `Hanseg2023Algorithm` class, include additional scripts and import all the required python packages. When adding additional scripts, make sure to add them to the `COPY` command in the [Dockerfile](Dockerfile) so that they are included in the container. All the required python packages should be listed in the [requirements.txt](requirements.txt) file so that they are installed the container is built on the grand-challenges server.


Most likely you will need a different base image to build your container (e.g., Tensorflow instead of Pytorch, or a different version). This can be achieved by changing the `FROM` command in the [Dockerfile](Dockerfile), e.g. `FROM nvcr.io/nvidia/pytorch:22.12-py3` for Pytorch.\
Model weights and other files should also copied to the container using the `COPY` command (same as for additional scripts), see [Dockerfile](Dockerfile#L26) (line 26).

## 4. Building your container <a name="build"></a>

To test if all dependencies are met, you should run the file `build.bat` (Windows) / `build.sh` (Linux) to build the docker container. Please note that the next step (testing the container) also runs a build, so this step is not mandatory if you are certain that everything is set up correctly.

## 5. Testing your container <a name="test"></a>

To test your container, you should run `test.bat` (on Windows) or `test.sh` (on Linux, might require sudo priviledges). This will run the test image(s) provided in the test folder through your model. 
## 6. Generating the bundle for uploading your algorithm <a name="export"></a>

Finally, you need to run the `export.sh` (Linux) or `export.bat` script to package your docker image. This step creates a file with the extension "tar.gz", which you can then upload to grand-challenge to submit your algorithm.

## 7. Creating an "Algorithm" on GrandChallenge and submitting your solution to the HaN-Seg 2023 Challenge

** Note: Submission to grand-challenge.org will open on March 23th. **

In order to submit your docker container, you first have to add an **Algorithm** entry for your docker container [here](https://han-seg2023.grand-challenge.org/evaluation/preliminary-test-phase/submissions/create/).


After saving, you can add your docker container (you can also overwrite your container here):

![uploadcontainer](https://user-images.githubusercontent.com/10051592/128370733-7445e252-a354-4c44-9155-9f232cd9f220.jpg)

Please note that it can take a while (several minutes) until the container becomes active. You can determine which one is active in the same dialog:

![containeractive](https://user-images.githubusercontent.com/10051592/128373241-83102a43-aad7-4457-b068-a6c7cc5a3b98.jpg)

You can also try out your algorithm. Please note that you will require an image that has the DPI property set in order to use this function. You can use the image test/007.tiff provided as part of this container as test image.

![tryout](https://user-images.githubusercontent.com/10051592/128373614-30b76cf6-2b2d-4d5d-87db-b8c67b47b64f.jpg)

Finally, you can submit your docker container to MIDOG:

![submit_container](https://user-images.githubusercontent.com/10051592/128371715-d8385754-806e-4420-ac5e-4c25cc38112a.jpg)

## General remarks
- The training is not done as part of the docker container, so please make sure that you only run inference within the container.


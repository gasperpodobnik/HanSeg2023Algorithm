#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
OUTDIR=$SCRIPTPATH/output

./build.sh

# Maximum is currently 30g, configurable in your algorithm image settings on grand challenge
MEM_LIMIT="4g"

# create output dir if it does not exist
if [ ! -d $OUTDIR ]; then
  mkdir $OUTDIR;
fi

# Do not change any of the parameters to docker run, these are fixed
docker run --rm \
        --memory="${MEM_LIMIT}" \
        --memory-swap="${MEM_LIMIT}" \
        --network="none" \
        --cap-drop="ALL" \
        --security-opt="no-new-privileges" \
        --shm-size="128m" \
        --pids-limit="256" \
        -v $SCRIPTPATH/test/:/input/ \
        -v $OUTDIR:/output/ \
        hanseg2023algorithm


echo
echo
echo "Compare files in $OUTDIR with the expected results to see if test is successful"
docker run --rm \
        -v $OUTDIR:/output/ \
        python:3.8-slim ls -al /output/images/head_neck_oar
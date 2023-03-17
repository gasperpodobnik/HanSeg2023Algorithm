#!/usr/bin/env bash

./build.sh

docker save hanseg2023algorithm | gzip -c > HanSeg2023Algorithm.tar.gz

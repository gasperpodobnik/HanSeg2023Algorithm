#!/usr/bin/env bash
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# docker build --no-cache -t hanseg2023algorithm "$SCRIPTPATH"
docker build -t hanseg2023algorithm "$SCRIPTPATH"

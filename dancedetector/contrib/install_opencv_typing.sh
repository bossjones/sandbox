#!/usr/bin/env bash

set -x

# get_cv2_path(){


# }

_DIR=`python3 -c 'import cv2, os;print(os.path.dirname(cv2.__file__))'`

echo "_DIR=${_DIR}"


# https://github.com/opencv/opencv/issues/14590#issuecomment-873003116
curl -sSL https://raw.githubusercontent.com/bossjones/python-type-stubs/add-opencv/cv2/__init__.pyi > "${_DIR}/cv2.pyi"

ls -lta "${_DIR}/cv2.pyi"

set +x

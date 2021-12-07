# USAGE
# python rotate.py --image ../images/trex.png
import argparse

from typing import Any, Union

# from cv2 import cv2
import cv2
import imutils
# Import the necessary packages
import numpy as np

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

# Load the image and show it
# SOURCE: https://stackoverflow.com/questions/56611983/type-hints-and-chained-assignment-and-multiple-assignments
image: Union[np.ndarray, Any]

image = cv2.imread(args["image"])
cv2.imshow("Original", image)

# Grab the dimensions of the image and calculate the center
# of the image
(h, w) = image.shape[:2]
# Integer division is used here, denoted as "//" to ensure we receive whole integer numbers.
center = (w // 2, h // 2)

# Rotate our image by 45 degrees
M = cv2.getRotationMatrix2D(center, 45, 1.0)
rotated = cv2.warpAffine(image, M, (w, h))
cv2.imshow("Rotated by 45 Degrees", rotated)

# Rotate our image by -90 degrees
M = cv2.getRotationMatrix2D(center, -90, 1.0)
rotated = cv2.warpAffine(image, M, (w, h))
cv2.imshow("Rotated by -90 Degrees", rotated)

# Finally, let's use our helper function in imutils.py to
# rotate the image by 180 degrees (flipping it upside down)
rotated = imutils.rotate(image, 180)
cv2.imshow("Rotated by 180 Degrees", rotated)
cv2.waitKey(0)

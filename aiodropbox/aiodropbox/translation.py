# USAGE
# python translation.py --image ../images/trex.png

import argparse

from cv2 import cv2
import imutils
# Import the necessary packages
import numpy as np

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

# Load the image and show it
image = cv2.imread(args["image"])
cv2.imshow("Original", image)

# NOTE: Translating (shifting) an image is given by a
# NumPy matrix in the form:
# 	[[1, 0, shiftX], [0, 1, shiftY]]
# You simply need to specify how many pixels you want
# to shift the image in the X and Y direction.
# Let's translate the image 25 pixels to the right and
# 50 pixels down
# ------------------------------------------------
# 1. We first define our translation matrix M.
# This matrix tells us how many pixels to the left or right, and up or down, the image will be shifted.
# ------------------------------------------------
M = np.float32([[1, 0, 25], [0, 1, 50]])
shifted = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
cv2.imshow("Shifted Down and Right", shifted)

# Now, let's shift the image 50 pixels to the left and
# 90 pixels up. We accomplish this using negative values(shift to left)
M = np.float32([[1, 0, -50], [0, 1, -90]])
shifted = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
cv2.imshow("Shifted Up and Left", shifted)

# Finally, let's use our helper function in imutils.py to
# shift the image down 100 pixels
shifted = imutils.translate(image, 0, 100)
cv2.imshow("Shifted Down", shifted)
cv2.waitKey(0)

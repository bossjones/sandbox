# USAGE
# python identify_meme.py --image ../images/beach.png
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html
# SEE: https://umar-yusuf.blogspot.com/2020/04/crop-images-using-python-opencv-module.html

import pathlib

from typing import Any, Union

from IPython.display import display
from PIL import Image
import cv2
import imutils
import mahotas
# Import the necessary packages
from matplotlib import pyplot as plt
# Import the necessary packages
import numpy as np

# Construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="Path to the image")
# args = vars(ap.parse_args())

args = {}

current_folder = pathlib.Path(
    f"/Users/malcolm/dev/bossjones/aiodropbox/notebooks"
)
# print(current_folder)

# # Calculating path to the input data
args["image"] = pathlib.Path(f"{current_folder.parent}/images/IMG_8831.PNG").resolve()

# print(args["image"])

assert args["image"].exists()

# SOURCE: http://engineering.curalate.com/2017/04/13/content-based-intelligent-cropping.html


def showImage(img):
    # plt.axis('off')
    # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    temp_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converting BGR to RGB

    # SOURCE: https://gist.github.com/mstfldmr/45d6e47bb661800b982c39d30215bc88
    display(Image.fromarray(temp_image))


# _image = f"{args['image']}"
image: Union[np.ndarray, Any]
# # # Load the image and show it
image = cv2.imread(f"{args['image']}")

# In Pillow, the order of colors is assumed to be RGB (red, green, blue).
# As we are using Image.fromarray() of PIL module, we need to convert BGR to RGB.
temp_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Converting BGR to RGB

# SOURCE: https://gist.github.com/mstfldmr/45d6e47bb661800b982c39d30215bc88
display(Image.fromarray(temp_image))

image.shape

# Load the image, convert it to grayscale, and blur it slightly
# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (11, 11), 0)

print("gray")
# SOURCE: https://gist.github.com/mstfldmr/45d6e47bb661800b982c39d30215bc88
display(Image.fromarray(gray))


print("blurred-gray")
# SOURCE: https://gist.github.com/mstfldmr/45d6e47bb661800b982c39d30215bc88
display(Image.fromarray(blurred))

# Find contours in the edged image.
# NOTE: The cv2.findContours method is DESTRUCTIVE to the image
# you pass in. If you intend on reusing your edged image, be
# sure to copy it before calling cv2.findContours# The first thing we are going to do is apply edge detection to
# the image to reveal the outlines of the coins
edged = cv2.Canny(blurred, 30, 150)

# SOURCE: https://gist.github.com/mstfldmr/45d6e47bb661800b982c39d30215bc88
display(Image.fromarray(edged))
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)


# How many contours did we find?
print("I count {} objects in this image".format(len(cnts)))

# Find contours in the edged image.
# NOTE: The cv2.findContours method is DESTRUCTIVE to the image
# you pass in. If you intend on reusing your edged image, be
# sure to copy it before calling cv2.findContours# The first thing we are going to do is apply edge detection to
# the image to reveal the outlines of the coins
edged = cv2.Canny(blurred, 30, 150)

# SOURCE: https://gist.github.com/mstfldmr/45d6e47bb661800b982c39d30215bc88
display(Image.fromarray(edged))
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)


# How many contours did we find?
print("I count {} objects in this image".format(len(cnts)))

# Now, let's loop over each contour
for (i, c) in enumerate(cnts):
    # We can compute the 'bounding box' for each contour, which is
    # the rectangle that encloses the contour
    (x, y, w, h) = cv2.boundingRect(c)

    # Now that we have the contour, let's extract it using array
    # slices
    print("Coin #{}".format(i + 1))
    coin = image[y : y + h, x : x + w]
    display(Image.fromarray(coin))

    # Just for fun, let's construct a mask for the coin by finding
    # The minumum enclosing circle of the contour
    mask = np.zeros(image.shape[:2], dtype="uint8")
    ((centerX, centerY), radius) = cv2.minEnclosingCircle(c)
    cv2.circle(mask, (int(centerX), int(centerY)), int(radius), 255, -1)
    mask = mask[y : y + h, x : x + w]
    display(Image.fromarray(cv2.bitwise_and(coin, coin, mask=mask)))

# SOURCE: http://engineering.curalate.com/2017/04/13/content-based-intelligent-cropping.html


def drawRegions(source, res, regions, color=(0, 0, 255), size=4):
    for (x, y, w, h) in regions:
        res[y : y + h, x : x + w] = source[y : y + h, x : x + w]
        cv2.rectangle(res, (x, y), (x + w, y + h), color, size)
    return res


faded = (image * 0.65).astype(np.uint8)

interestPoints = cv2.goodFeaturesToTrack(
    gray, maxCorners=200, qualityLevel=0.01, minDistance=20
).reshape(-1, 2)
interestPointRegions = np.concatenate(
    (interestPoints, np.ones(interestPoints.shape)), axis=1
).astype(np.int32)
showImage(
    drawRegions(image, faded.copy(), interestPointRegions, (255, 255, 255), size=10)
)

input_img_path = pathlib.Path(
    f"{current_folder.parent}/images/exampleImages/input.jpg"
).resolve()

# SOURCE: https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_gui/py_image_display/py_image_display.html
# Second argument is a flag which specifies the way image should be read.

# cv2.IMREAD_COLOR : Loads a color image. Any transparency of image will be neglected. It is the default flag.
# cv2.IMREAD_GRAYSCALE : Loads image in grayscale mode
# cv2.IMREAD_UNCHANGED : Loads image as such including alpha channel

input_img = cv2.imread(f"{input_img_path}", cv2.IMREAD_GRAYSCALE)
showImage(input_img)

prod_img = pathlib.Path(
    f"{current_folder.parent}/images/exampleImages/product.jpg"
).resolve()

assert prod_img.exists()


# SOURCE: https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_gui/py_image_display/py_image_display.html
# Second argument is a flag which specifies the way image should be read.

# cv2.IMREAD_COLOR : Loads a color image. Any transparency of image will be neglected. It is the default flag.
# cv2.IMREAD_GRAYSCALE : Loads image in grayscale mode
# cv2.IMREAD_UNCHANGED : Loads image as such including alpha channel

productImage = cv2.imread(f"{prod_img}", cv2.IMREAD_GRAYSCALE)

showImage(productImage)

# # SOURCE = https://opencv24-python-tutorials.readthedocs.io/en/stable/py_tutorials/py_feature2d/py_matcher/py_matcher.html
# # Initiate SIFT detector
detector = cv2.SIFT()

# # find the keypoints and descriptors with SIFT
kpts1, descs1 = detector.detectAndCompute(productImage, None)
# kpts2, descs2 = detector.detectAndCompute(input_img, None)

# matches = [m for (m, n) in flann.knnMatch(descs1, descs2, k=2) if m.distance < 0.8 * n.distance]
# sourcePoints = np.float32([kpts1[m.queryIdx].pt for m in matches]).reshape(-1, 2)
# destPoints = np.float32([kpts2[m.trainIdx].pt for m in matches]).reshape(-1, 2)
# M, mask = cv2.findHomography(sourcePoints, destPoints, cv2.RANSAC, 11.0)# matches = [m for (m, n) in flann.knnMatch(descs1, descs2, k=2) if m.distance < 0.8 * n.distance]
# sourcePoints = np.float32([kpts1[m.queryIdx].pt for m in matches]).reshape(-1, 2)
# destPoints = np.float32([kpts2[m.trainIdx].pt for m in matches]).reshape(-1, 2)
# M, mask = cv2.findHomography(sourcePoints, destPoints, cv2.RANSAC, 11.0)

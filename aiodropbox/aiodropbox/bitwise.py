# USAGE
# python bitwise.py

# Bitwise operations operate in a binary manner and are
# represented as grayscale images. A given pixel is turned
# 'off' if it has a value of zero, and it is turned 'on' if the
# pixel has a value greater than zero.

from cv2 import cv2
# Import the necessary packages
import numpy as np

# First, let's draw a rectangle
rectangle = np.zeros((300, 300), dtype="uint8")
cv2.rectangle(rectangle, (25, 25), (275, 275), 255, -1)
cv2.imshow("Rectangle", rectangle)

# Secondly, let's draw a circle
circle = np.zeros((300, 300), dtype="uint8")
cv2.circle(circle, (150, 150), 150, 255, -1)
cv2.imshow("Circle", circle)

# A bitwise 'AND' is only True when both rectangle
# and circle have a value that is 'ON'. Simply put,
# the bitwise_and function examines every pixel in
# rectangle and circle. If both pixels have a value
# greater than zero, that pixel is turned 'ON' (i.e
# set to 255 in the output image). If both pixels
# are not greater than zero, then the output pixel
# is left 'OFF' with a value of 0.
bitwiseAnd = cv2.bitwise_and(rectangle, circle)
cv2.imshow("AND", bitwiseAnd)
cv2.waitKey(0)

# A bitwise 'OR' examines every pixel in rectangle
# and circle. If EITHER pixel in rectangle or circle
# is greater than zero, then the output pixel has a
# value of 255, otherwise it is 0.
bitwiseOr = cv2.bitwise_or(rectangle, circle)
cv2.imshow("OR", bitwiseOr)
cv2.waitKey(0)

# The bitwise 'XOR' is identical to the 'OR' function,
# with one exception: both rectangle and circle are
# not allowed to have values greater than 0.
bitwiseXor = cv2.bitwise_xor(rectangle, circle)
cv2.imshow("XOR", bitwiseXor)
cv2.waitKey(0)

# Finally, the bitwise 'NOT' inverts the values of
# the pixels. Pixels with a value of 255 become 0,
# and pixels with a value of 0 become 255.
bitwiseNot = cv2.bitwise_not(circle)
cv2.imshow("NOT", bitwiseNot)
cv2.waitKey(0)

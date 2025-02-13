import numpy as np
import cv2
from matplotlib import pyplot as plt
import ContourMethoden

cap = cv2.VideoCapture('../../Data/Dokumentation/AW_Teile_mit_OpenCV_erkennen/Eingabe_Bilder/10.jpg')
ret, image = cap.read()

# print(ret)  # Debug if image was loaded correctly

outer_contour, inner_contour = ContourMethoden.get_contours(image)

outer_contour = np.array(outer_contour)
inner_contour = np.array(inner_contour)

#######################################################################################
plt.figure(figsize=(15, 15))
plt.imshow(image)  # Wrong color space

# print(outer_contour)
# type(outer_contour)

# Debug-method for creating and displaying the mask
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Soft focus to get rid of any noise
img = cv2.GaussianBlur(image, (5, 5), 0)

# Convert BGR to HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 2 masks because red in HSV is at the beginning and end
mask1 = cv2.inRange(hsv, lower_red, upper_red)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

# Merge masks
mask = mask1 + mask2

plt.figure(figsize=(15, 15))
plt.imshow(mask)  # Wrong color space (because of matplotlib)

# Calculate outer HuMoments
moments = cv2.moments(outer_contour[0])
outer_huMoments = cv2.HuMoments(moments)

# Calculate inner HuMoments
# moments = cv2.moments(inner_contour[0])
# inner_huMoments = cv2.HuMoments(moments)

# Debug
# print("huMoments Außen:", huMoments_aussen)
# print("huMoments Innen:", huMoments_innen)

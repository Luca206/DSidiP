import cv2

# Minimum area of the contours in pixel:
min_area = 2000

def get_contours(mask):
    outer_contours = []
    inner_contours = []

    # Find contours
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Get the coordinates of the contours here and divide into inner and outer contours
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > min_area:
            if hierarchy[0][i][3] == -1: # -1 = outer contour
                outer_contours.append(contour)
            else: # inner contour
                inner_contours.append(contour)

    return outer_contours, inner_contours

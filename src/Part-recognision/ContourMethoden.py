import cv2

# Mindestfläche der Contouren in Pixel:
min_area = 2000

outer_contours = []
inner_contours = []

def getContours(mask):
    # Konturen finden
    Contours, hirarchie = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Bekomme hier die Koordinaten der Konturen und teile in innere und äußere Contouren
    for i, contour in enumerate(Contours):
        area = cv2.contourArea(contour)
        if area > min_area:
            if hirarchie[0][i][3] == -1: # -1 = äußere Kontur
                outer_contours.append(contour)
            else: # innere Kontur
                inner_contours.append(contour)

    return outer_contours, inner_contours
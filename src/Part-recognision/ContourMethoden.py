import numpy as np
import cv2

#setze Farbgrenzen für ROT (2 stück weil in HSV oben und unten)
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

lower_red2 = np.array([170, 120, 70])
upper_red2= np.array([180, 255, 255])

#MindestFläche der Contouren in Pixel:
min_area = 2000

outer_contours = []
inner_contours = []

def getContours(img):

    #mache ein weichzeichen um rauschen los zu werden
    img = cv2.GaussianBlur(img, (5, 5), 0)

    #Rufe Contours auf:
    # konvertiere von BGR zu HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2 Masken weil rot in HSV am anfang und ende liegt
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    # Füge beide Masken zusammen
    mask = mask1 + mask2

    #Konturen finden
    Contours, hirarchie = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #bekomme hier die Koordinaten der Konturen und teile in innere und äußere Contouren
    for i, contour in enumerate(Contours):
        area = cv2.contourArea(contour)
        if area > min_area:
            if hirarchie[0][i][3] == -1: #-1 = äußere Kontur
                outer_contours.append(contour)
            else: #innere Kontur
                inner_contours.append(contour)

    return outer_contours, inner_contours
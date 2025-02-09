import numpy as np
import cv2

#setze Farbgrenzen für ROT (2 stück weil in HSV oben und unten)
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

lower_red2 = np.array([170, 120, 70])
upper_red2= np.array([180, 255, 255])

#MindestGröße der Contouren:
minarea = 2000

outer_contours = []
inner_contours = []

#frame = cv2.flip(frame, 1)

def createRedMask(img):
    #mache ein weichzeichen um rauschen los zu werden
    img = cv2.GaussianBlur(img, (5, 5), 0)


    #Rufe Contours auf:
    Contours, hirarchie, mask = createContours(img)

    #einzeichnen der BoundingBoxen
    #bekomme hier die Koordinaten der Boundingboxen
    for i, contour in enumerate(Contours):
        area = cv2.contourArea(contour)
        if area > minarea:
            if hirarchie[0][i][3] == -1: #-1 = äußere Kontur
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                #print(f"Kontur: {contour}")

                outer_contours.append(contour)

                #Zeichne COntour ins bild ein
                cv2.drawContours(img, [contour], -1, (255, 0, 0), 1) #-1 ist alle Contouren, blauer Farbton, Dicke 1
            else: #innere Kontur

                inner_contours.append(contour)
                cv2.drawContours(img, [contour], -1, (255, 255, 0), 1)

            #print("Äußere Kontur:", outer_contours[0])  #printet erste äußere kontur
            #print("Innere Kontur:", inner_contours[0])

    #Anwenden der maske aufs Originalbild
    mask = cv2.bitwise_and(img, img, mask=mask)

    return img, mask


def createContours(img):
    # konvertiere von BGR(openCV) zu HSV ???
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2 Masken weil rot in HSV am anfang und ende liegt
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    # Füge beide Masken zusammen
    mask = mask1 + mask2

    #BoundingBoxen finden
    Contours, hirarchie = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return Contours, hirarchie, mask
import numpy as np
import cv2
from matplotlib import pyplot as plt
import ContourMethoden

cap = cv2.VideoCapture('..\\..\\Data\\Dokumentation\\AW_Teile_mit_OpenCV_erkennen\\Eingabe_Bilder\\07.jpg')
ret, image = cap.read()

# print(ret)  #debug ob bild erfolgreich geladen wurde

Kontur_aussen, Kontur_innen = ContourMethoden.getContours(image)

Kontur_aussen = np.array(Kontur_aussen)
Kontur_innen = np.array(Kontur_innen)

plt.figure(figsize=(15, 15))
plt.imshow(image)  # Farbraum ist falsch weil matpltlib aber ist egal

# print(Kontur_aussen)
# type(Kontur_aussen)

# Methode zum erstellen und anzeigen der Maske, für debug-zwecke
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# mache ein weichzeichen um rauschen los zu werden
img = cv2.GaussianBlur(image, (5, 5), 0)

# Rufe Contours auf:
# konvertiere von BGR zu HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# 2 Masken weil rot in HSV am anfang und ende liegt
mask1 = cv2.inRange(hsv, lower_red, upper_red)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

# Füge beide Masken zusammen
mask = mask1 + mask2

plt.figure(figsize=(15, 15))
plt.imshow(mask)  # Farbraum falsch weil matpltlib

# Calculate Moments
moments = cv2.moments(Kontur_aussen[0])
# Calculate Hu Moments
huMoments_aussen = cv2.HuMoments(moments)

# Die inneren Hu-Momente brauchen wir ja nicht eigentlich

# Calculate Moments
# moments = cv2.moments(Kontur_innen[0])
# Calculate Hu Moments
# huMoments_innen = cv2.HuMoments(moments)

# print("huMoments Außen:", huMoments_aussen)
# print("huMoments Innen:", huMoments_innen)

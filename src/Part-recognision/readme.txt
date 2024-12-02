Die localmain.py ist eigentlich nur zum testen, wenn die IDS Kamera nicht verfügbar ist.
utils_camera.py enthält die Methdoen um aufs Kamerabild zuzugreifen
ContourMethoden.py enthält die Methode zum generieren der Konturen und Maske des Bildes
--> Input: Kamerabild, Output: Liste outer Contours und Liste inner Contours und vllt Maske(falls nötig)


main.py hier sollen dann die Teile erkannt werden

ToDO:
einlesen JSON
bestimmen der Teile ID
erkennung der Rotation mit Hilfe von Aruco marker
--> Winkel der längsten Kante zu Bais
berechnung Ansaugkoordinaten
Senden der Bild cords zum Docker
--> Output: cords Teil, ZielCords, Zeilrotation
Umrechnung Bild cords zu Robo cords soll im Docker gemacht werden

# <------------------------------------------------------------------------------------------------------>
#
# (Mit [TODO] ist unter anderem gemeint, dass sich der Arbeitsschritt noch nicht in der main.py befindet.)
#
# [DONE] 1. Bild einlesen
# [DONE] 2. Maske berechnen
# [DONE] 3. Äußere (und innere) Kontur(en) bestimmen
#
# [DONE] 4.1 Innere Kontur existiert nicht (-> Keine Bohrung)
# [DONE]     4.1.1 Bild-Momente berechnen
# [DONE]     4.1.2 Hu-Momente berechnen
# [DONE]     4.1.3 Teil anhand der Hu-Momente eindeutig bestimmen
#                  (mit Ausnahme von Teilen "01-09" und "01-11" aus offensichtlichen Gründen)
# [DONE]     4.1.4 (Geometrischen) Schwerpunkt (mit Hilfe der Konturen) berechnen
#                  -> Punkt zum Greifen durch Roboter
#
# [TODO] 4.2 Innere Kontur existiert (-> Bohrung)
# [TODO]     4.2.1 Zwischen den Teilen "01-01" und "01-02" differenzieren
#                  (In unserem Anwendungsfall die einzigen Teile mit Bohrung)
# [DONE]     4.2.2 Bestimmen, welcher Punkt am weitesten vom Rand entfernt ist,
#                  da (geometrischer) Schwerpunkt in Bohrung liegen kann
#                  (Euklidische Distanztransformation)
#                  -> Punkt zum Greifen durch Roboter
#
# [TODO] 5. Rotation des Teils berechnen (aktueller Ansatz: ArUco Marker)
#           -> Gradmaß für Gegenrotation durch Roboter
# [TODO] 6. Zielkoordinaten bzw. Punkt zum Loslassen der Teile bestimmen
# [TODO] 7. Punkt zum Greifen, Punkt zum Loslassen und Gradmaß für Gegenrotation an Roboter senden
#
# <------------------------------------------------------------------------------------------------------>

from utils_camera import Camera
import centroid as c
import ComponentComparer as cc
import ContourMethoden as cm
import createMask
import cv2 as cv
import euclideanDistanceTransform as edt
import numpy as np
#import time

# DirectX, DirectShow o.ä. zum Streamen zum Docker, weil die Kamera nicht über USB erkannt wird

# Client
class Application:
    def __init__(self):
        self.camera = Camera()

    def run(self):
        # Initialisiere die Kamera
        self.camera.start_camera()
        
        try:
            # Endlosschleife für den Live-Stream mit 10 fps
            while True:
                # 1. Bild einlesen
                img = self.camera.get_current_frame()

                # 2. Maske berechnen
                lower_red = np.array([0, 120, 70])
                upper_red = np.array([10, 255, 255])

                lower_red2 = np.array([170, 120, 70])
                upper_red2 = np.array([180, 255, 255])

                mask = createMask.createMaskBGR2HSV(img = img,
                                                    lower_b = lower_red,
                                                    upper_b = upper_red,
                                                    lower_b_2 = lower_red2,
                                                    upper_b_2 = upper_red2)

                # 3. Äußere (und innere) Kontur(en) bestimmen
                outer_contours, inner_contours = cm.getContours(mask)

                # 4.1 Innere Kontur existiert nicht (-> Keine Bohrung)
                if len(inner_contours) == 0:
                    # 4.1.1 Bild-Momente berechnen
                    moments = cv.moments(outer_contours[0])

                    # 4.1.2 Hu-Momente berechnen
                    huMoments_aussen = cv.HuMoments(moments)

                    # 4.1.3 Teil anhand der Hu-Momente eindeutig bestimmen
                    #       (mit Ausnahme der Teile "01-09" und "01-11" aus offensichtlichen Gründen)
                    tile_label = cc.find_most_similar_hu_moments(huMoments_aussen)

                    # 4.1.4 (Geometrischen) Schwerpunkt (mit Hilfe der Konturen) berechnen
                    #       -> Punkt zum Greifen durch Roboter
                    grabbing_point = c.determine_centroid_from_contour(inner_contours)
                    """ outer_centroid = c.determine_centroid_from_moments(moments) """ # NOTE: Schwerpunkt alternativ über Bild-Momente berechenbar

                # [TODO] 4.2 Innere Kontur existiert (-> Bohrung)
                else:
                    # [TODO] 4.2.1 Zwischen den Teilen "01-01" und "01-02" differenzieren
                    #              (In unserem Anwendungsfall die einzigen Teile mit Bohrung)
                    threshold = ... # NOTE: Muss noch ermittelt werden, hängt (unter anderem) vom Kamerabild ab.
                                    #       Voraussichtlich halbe euklidische Distanz vom äußeren zum inneren
                                    #       Schwerpunkt des Teils "01-01" (außermittige Bohrung).
                    outer_centroid = c.determine_centroid_from_contour(outer_contours)
                    inner_centroid = c.determine_centroid_from_contour(inner_contours)
                    distance = np.linalg.norm(np.array(outer_centroid) - np.array(inner_centroid))
                    if distance >= threshold:
                        tile_label = "01-01"
                    else:
                        tile_label = "01-02"

                    # 4.2.2 Bestimmen, welcher Punkt am weitesten vom Rand entfernt ist,
                    #       da (geometrischer) Schwerpunkt in Bohrung liegen kann
                    #       (Euklidische Distanztransformation)
                    #       -> Punkt zum Greifen durch Roboter
                    grabbing_point = edt.euclideanDistanceTransform(mask)

                # [TODO] 5. Rotation des Teils berechnen (aktueller Ansatz: ArUco Marker)
                #           -> Gradmaß für Gegenrotation durch Roboter
                ...

                # [TODO] 6. Zielkoordinaten bzw. Punkt zum Loslassen der Teile bestimmen
                ...

                # [TODO] 7. Punkt zum Greifen, Punkt zum Loslassen und Gradmaß für Gegenrotation an Roboter senden
                ...

# <------------------------------------------------------------------------------------------------------------------------------------------------>

                # Versuch, das Bild auf die Bildschirmgröße anzupassen
                # Nur zum Anzeigen, kann ansonsten entfernt werden
                img = cv.resize(img, (1080, 1920))

                # Zeige das Bild in einem Fenster an
                cv.imshow('Original Bild', img)
                
                # Warte 100 ms für ca. 10 fps und beende die Schleife bei Tastendruck 'q'
                if cv.waitKey(100) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("Programm wird beendet...")
        
        finally:
            # Stoppen der Kamera und Schließen des Fensters
            self.camera.stop_camera()
            cv.destroyAllWindows()

# Start application
if __name__ == "__main__":
    app = Application()
    app.run()

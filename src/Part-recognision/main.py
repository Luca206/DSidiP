# <------------------------------------------------------------------------------------------------------>
#
#  1. Bild einlesen
#  2. Maske berechnen
#  3. Äußere (und innere) Kontur(en) bestimmen
#
#  4.1 Innere Kontur existiert nicht (-> Keine Bohrung)
#      4.1.1 Bild-Momente berechnen
#      4.1.2 Hu-Momente berechnen
#      4.1.3 Teil anhand der Hu-Momente eindeutig bestimmen
#                  (mit Ausnahme von Teilen "01-09" und "01-11")
#      4.1.4 (Geometrischen) Schwerpunkt (mit Hilfe der Konturen) berechnen
#                  -> Punkt zum Greifen durch Roboter
#
#  4.2 Innere Kontur existiert (-> Bohrung)
#      4.2.1 Zwischen den Teilen "01-01" und "01-02" differenzieren
#                  (In unserem Anwendungsfall die einzigen Teile mit Bohrung)
#      4.2.2 Bestimmen, welcher Punkt am weitesten vom Rand entfernt ist,
#                  da (geometrischer) Schwerpunkt in Bohrung liegen kann
#                  (Euklidische Distanztransformation)
#                  -> Punkt zum Greifen durch Roboter
#
#  5. Rotation des Teils berechnen (aktueller Ansatz: ArUco Marker)
#           -> Gradmaß für Gegenrotation durch Roboter
#  6. Zielkoordinaten bzw. Punkt zum Loslassen der Teile bestimmen
#  7. Punkt zum Greifen, Punkt zum Loslassen und Gradmaß für Gegenrotation an Roboter senden
#
# <------------------------------------------------------------------------------------------------------>

from utils_camera import Camera
import cv2
import createMask
import numpy as np
import ContourMethoden
import centroid
import ComponentComparer
import euclideanDistanceTransform

# DirectX oder DirectShow oder so zum Streamen zum Docker
# weil die Kamera nicht über USB erkannt wird

# Methode der Teile-Erkennung:
#  True für ArUcoMarker
#  False für Maske (es werden trotzdem ArUco Marker für die relative Position verwendet)

useAruco = True

lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])


def send_to_robot(id, x_rel, y_rel, rotation):

    # Hier kommt der Code zum senden der Daten zum Roboter rein :)

    print("Folgende Daten wurden erfolgreich gesendet:")
    print("ID:", id, "x_rel: ", x_rel, "y_rel: ", y_rel, "Rotation: ", rotation)

    return 1


# Client
class Application:

    def __init__(self):
        self.camera = Camera()

    def run(self):
        # Initialisiere die Kamera
        self.camera.start_camera()

        try:
            # Endlosschleife für den Live-Stream mit 10 FPS
            anchor_a_x = None
            anchor_a_y = None
            anchor_b_x = None
            anchor_b_y = None
            current_marker = None
            delay = 1

            while True:
                # Hole das aktuelle Bild von der Kamera
                image = self.camera.get_current_frame()
                # image = cv2.imread('hilfe2.jpg')

                # Lade das ArUco-Dictionary
                aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
                parameters = cv2.aruco.DetectorParameters()

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Erkenne die Marker
                detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
                corners, ids, rejected_img_points = detector.detectMarkers(gray)

                # ids = None
                if ids is not None:
                    for i in range(len(ids)):
                        id = ids[i][0]

                        # Setze Koordinaten für Ankerpunkte, falls noch nicht gesetzt
                        if id == 42:
                            anchor_a_x, anchor_a_y = corners[i][0][0][0], corners[i][0][1][1]
                        if id == 69:
                            anchor_b_x, anchor_b_y = corners[i][0][0][0], corners[i][0][1][1]

                        # Gehe sicher, dass nicht Daten für den selben Punkt mehrmals gesendet werden
                        delay = delay + 1

                    # Nutze Maske
                    if not useAruco:

                        if (delay > 30) \
                                and (anchor_a_x is not None) \
                                and (anchor_b_x is not None):

                            # Methode zum Erstellen der Red Maske:
                            mask = createMask.create_mask_bgr2_hsv(img=image,
                                                                   lower_b=lower_red,
                                                                   upper_b=upper_red,
                                                                   lower_b_2=lower_red2,
                                                                   upper_b_2=upper_red2)

                            # Äußere (und innere) Kontur(en) bestimmen
                            outer_contours, inner_contours = ContourMethoden.get_contours(mask)

                            # Innere Kontur existiert nicht (= Keine Bohrung)
                            if len(inner_contours) == 0:
                                # Bild-Momente berechnen
                                moments = cv2.moments(outer_contours[0])

                                # Hu-Momente berechnen
                                hu_moments_outer = cv2.HuMoments(moments)

                                # Teil anhand der Hu-Momente bestimmen
                                tile_label = ComponentComparer.find_most_similar_hu_moments(hu_moments_outer)

                                # Schwerpunkt berechnen
                                grabbing_point = centroid.determine_centroid_from_contour(inner_contours)
                                """ outer_centroid = c.determine_centroid_from_moments(moments) """  # NOTE: Schwerpunkt alternativ über Bild-Momente berechenbar

                            # Innere Kontur existiert (= Bohrung)
                            else:
                                # Nicht mehr notwendig, da Teile bereits unterschieden werden
                                # Zwischen den Teilen "01-01" und "01-02" differenzieren
                                threshold = 22  # Halbe euklidische Distanz zwischen äußerem und innerem Schwerpunkt von Teil "01-01"
                                outer_centroid = centroid.determine_centroid_from_contour(outer_contours)
                                inner_centroid = centroid.determine_centroid_from_contour(inner_contours)
                                distance = np.linalg.norm(np.array(outer_centroid) - np.array(inner_centroid))
                                if distance >= threshold:
                                    tile_label = "01-01"
                                else:
                                    tile_label = "01-02"

                                # Bestimmen, welcher Punkt am weitesten vom Rand entfernt ist
                                grabbing_point = euclideanDistanceTransform.euclidean_distance_transform(mask)

                            # Initialisiere eine Liste für die Eckpunkte
                            corner_points = []

                            # Iteriere durch die Konturen
                            for contour in outer_contours:
                                # Verwende die Approximation, um die Eckpunkte zu finden
                                epsilon = 0.02 * cv2.arcLength(contour, True)
                                approx = cv2.approxPolyDP(contour, epsilon, True)

                                # Füge die Eckpunkte zur Liste hinzu
                                for point in approx:
                                    corner_points.append(point[0])
                                    # Zeichne die Eckpunkte auf dem Bild
                                    cv2.circle(image, tuple(point[0]), 5, (255, 0, 0), -1)

                            # Berechne die Kantenlängen zwischen den Eckpunkten
                            edges = []
                            for i in range(len(corner_points)):
                                pt1 = corner_points[i]
                                pt2 = corner_points[
                                    (i + 1) % len(corner_points)]  # Verbinde den letzten Punkt mit dem ersten
                                edge_length = np.linalg.norm(pt1 - pt2)
                                edges.append((pt1, pt2, edge_length))

                            # Bestimme die kürzeste Kante
                            shortest_edge = min(edges, key=lambda x: x[2])

                            # Berechnung des Anstiegs
                            m = (shortest_edge[1][1] - shortest_edge[0][0]) / \
                                (shortest_edge[1][1] - shortest_edge[0][0])

                            # Berechnung des Winkels in Radiant
                            theta = np.arctan(m)

                            # Umwandlung des Winkels in Grad
                            theta_degrees = np.degrees(theta)

                            # Berechnung der relativen Position in Prozent
                            x_rel = (grabbing_point[0] - anchor_a_x) / (anchor_b_x - anchor_a_x) * 100
                            y_rel = (grabbing_point[1] - anchor_a_y) / (anchor_b_y - anchor_a_y) * 100

                            # Sende alle daten zum roboter
                            id = tile_label
                            send_to_robot(id, x_rel, y_rel, theta_degrees)
                            delay = 1

                    # Nutze ArucoMarker
                    if useAruco:

                        if (id != current_marker) \
                                and (delay > 30) \
                                and (id != 42) \
                                and (id != 69) \
                                and (anchor_a_x is not None) \
                                and (anchor_b_x is not None):
                            current_marker = ids[i][0]
                            # Koordinaten der Punkte
                            x1, y1 = corners[i][0][0][0], corners[i][0][0][1]
                            x2, y2 = corners[i][0][1][0], corners[i][0][1][1]

                            # Berechnung des Anstiegs
                            m = (y2 - y1) / (x2 - x1)

                            # Berechnung des Winkels in Radiant
                            theta = np.arctan(m)

                            # Umwandlung des Winkels in Grad
                            theta_degrees = np.degrees(theta)

                            # Berechnung der relativen Position in Prozent
                            x_rel = (x1 - anchor_a_x) / (anchor_b_x - anchor_a_x) * 100
                            y_rel = (y1 - anchor_a_y) / (anchor_b_y - anchor_a_y) * 100

                            # Sende alle Daten zum Roboter
                            send_to_robot(id, x_rel, y_rel, theta_degrees)
                            delay = 1

                # Warte 100 ms für ca. 10 FPS und beende die Schleife bei Tastendruck 'q'
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("Programm wird beendet...")

        finally:
            # Stoppen der Kamera und Schließen des Fensters
            self.camera.stop_camera()
            cv2.destroyAllWindows()


# Start application
if __name__ == "__main__":
    app = Application()
    app.run()

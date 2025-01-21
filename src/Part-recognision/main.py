from utils_camera import Camera
import cv2
import FarbScanMethoden as fsm
import numpy as np
import ContourMethoden
import centroid
import ComponentComparer
import euclideanDistanceTransform
#from matplotlib import pyplot as plt

# DirectX oder DirectShow oder so zum Streamen zum Docker
# weil die Kamera nicht über USB erkannt wird

# Methode der Teile-erkennung:
#  True für ArUcoMarker
#  False für Maske (es werden trotzdem ArUco Marker für die relative Position verwendet)
useAruco = True

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
            # Endlosschleife für den Live-Stream mit 10 fps
            ankerA_x = None
            ankerA_y = None
            ankerB_x = None
            ankerB_y = None
            aktueller_marker = None
            delay = 1

            while True:
                # Hole das aktuelle Bild von der Kamera
                image = self.camera.get_current_frame()
                #image = cv2.imread('hilfe2.jpg')

                # Lade das ArUco-Dictionary
                aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
                parameters = cv2.aruco.DetectorParameters()

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Erkenne die Marker
                detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
                corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

                #ids = None
                if ids is not None:
                    #print("ids is  not None")
                    for i in range(len(ids)):
                        id = ids[i][0]
                        #print("bin in legth ids")
                        #print(id)

                        #setze Koordinaten für Aankerpunkte, falls noch nicht gesetzt
                        if id == 42:
                            #print(corners[i][0][0])
                            ankerA_x, ankerA_y = corners[i][0][0][0], corners[i][0][1][1]
                            #print("anker A gesetzt")
                        if id == 69:
                            ankerB_x, ankerB_y = corners[i][0][0][0], corners[i][0][1][1]
                            #print("anker B gesetzt")

                        #gehe sicher das nicht daten für den selben punkt mehrmals gesendet werden
                        #print(aktueller_marker)
                        delay = delay + 1
                        #print(delay)

                    # Nutze Maske
                    if not useAruco:

                        if (delay > 30) \
                            and (ankerA_x != None) \
                            and (ankerB_x != None):

                            #Methode zum erstellen der Red Maske:
                            img, mask = fsm.createRedMask(img)

                            # Äußere (und innere) Kontur(en) bestimmen
                            outer_contours, inner_contours = ContourMethoden.getContours(mask)

                            # Innere Kontur existiert nicht (= Keine Bohrung)
                            if len(inner_contours) == 0:
                                # Bild-Momente berechnen
                                moments = cv2.moments(outer_contours[0])

                                # Hu-Momente berechnen
                                huMoments_aussen = cv2.HuMoments(moments)

                                # Teil anhand der Hu-Momente bestimmen
                                tile_label = ComponentComparer.find_most_similar_hu_moments(huMoments_aussen)

                                # Schwerpunkt berechnen
                                grabbing_point = centroid.determine_centroid_from_contour(inner_contours)
                                """ outer_centroid = c.determine_centroid_from_moments(moments) """ # NOTE: Schwerpunkt alternativ über Bild-Momente berechenbar

                            # Innere Kontur existiert (= Bohrung)
                            else:
                                # Zwischen den Teilen "01-01" und "01-02" differenzieren
                                threshold = 22 # Halbe euklidische Distanz zwischen äußerem und innerem Schwerpunkt von Teil "01-01"
                                outer_centroid = centroid.determine_centroid_from_contour(outer_contours)
                                inner_centroid = centroid.determine_centroid_from_contour(inner_contours)
                                distance = np.linalg.norm(np.array(outer_centroid) - np.array(inner_centroid))
                                if distance >= threshold:
                                    tile_label = "01-01"
                                else:
                                    tile_label = "01-02"

                                # Bestimmen, welcher Punkt am weitesten vom Rand entfernt ist
                                grabbing_point = euclideanDistanceTransform.euclideanDistanceTransform(mask)

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
                                pt2 = corner_points[(i + 1) % len(corner_points)]  # Verbinde den letzten Punkt mit dem ersten
                                edge_length = np.linalg.norm(pt1 - pt2)
                                edges.append((pt1, pt2, edge_length))

                            # Bestimme die kürzeste Kante
                            shortest_edge = min(edges, key=lambda x: x[2])

                            # Berechnung des Anstiegs
                            m = (shortest_edge[1][1] - shortest_edge[0][0]) / \
                                (shortest_edge[1][1] - shortest_edge[0][0])

                            #print("m=", m)
                            # Berechnung des Winkels in Radiant
                            theta = np.arctan(m)
                            #print("theta=", theta)

                            # Umwandlung des Winkels in Grad
                            theta_degrees = np.degrees(theta)
                            #print("grad= ", theta_degrees)

                            # Berechnung der relativen Position in Prozent
                            x_rel = (grabbing_point[0] - ankerA_x) / (ankerB_x - ankerA_x) * 100
                            y_rel = (grabbing_point[1] - ankerA_y) / (ankerB_y - ankerA_y) * 100

                            #Sende alle daten zum roboter
                            id = tile_label
                            send_to_robot(id, x_rel, y_rel, theta_degrees)
                            delay = 1

                    # Nutze ArucoMarker
                    if useAruco:

                        if (id != aktueller_marker) \
                            and (delay > 30) \
                            and (id != 42) \
                            and (id != 69) \
                            and (ankerA_x != None) \
                            and (ankerB_x != None):
                            aktueller_marker = ids[i][0]
                            # Koordinaten der Punkte
                            x1, y1 = corners[i][0][0][0], corners[i][0][0][1]
                            x2, y2 = corners[i][0][1][0], corners[i][0][1][1]
                            #print("bin in neue id gefunden")

                            #print("x1:", x1, "y1:", y1)
                            #print("x2:", x2, "y2:", y2)

                            # Berechnung des Anstiegs
                            m = (y2 - y1) / (x2 - x1)

                            #print("m=", m)
                            # Berechnung des Winkels in Radiant
                            theta = np.arctan(m)
                            #print("theta=", theta)

                            # Umwandlung des Winkels in Grad
                            theta_degrees = np.degrees(theta)
                            #print("grad= ", theta_degrees)

                            # Berechnung der relativen Position in Prozent
                            x_rel = (x1 - ankerA_x) / (ankerB_x - ankerA_x) * 100
                            y_rel = (y1 - ankerA_y) / (ankerB_y - ankerA_y) * 100

                            #Sende alle daten zum roboter
                            
                            send_to_robot(id, x_rel, y_rel, theta_degrees)
                            delay = 1
                
                # Warte 100 ms für ca. 10 fps und beende die Schleife bei Tastendruck 'q'
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

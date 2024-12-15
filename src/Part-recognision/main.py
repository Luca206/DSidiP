#import time
from utils_camera import Camera
import cv2
import ContourMethoden as cm

# direct x oder direct show oder so zum streamen zum docker
# weil die kamera nicht über usb erkannt wird

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
                # Hole das aktuelle Bild von der Kamera
                img = self.camera.get_current_frame()

                #TODO mit äußeren Kontouren berechnen huMoments
                outer_contours, inner_contours = cm.getContours(img)

                #TODO Auslagerung der Vergleiche der Teile
                # Calculate Moments
                moments = cv2.moments(outer_contours[0])
                # Calculate Hu Moments
                huMoments_aussen = cv2.HuMoments(moments)

                #versuch bild auf Bildschirmgröße anzupassen
                #Nur zum anzeigen, sonst kann das raus
                img = cv2.resize(img,(1080,1920))

                # Zeige das Bild in einem Fenster an
                cv2.imshow('Original Bild', img)
                
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

#import time
from utils_camera import Camera
import cv2
import FarbScanMethoden as fsm

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

                #Methode zum erstellen der Red Maske:
                img, mask = fsm.createRedMask(img)
                
                #versuch bild auf Bildschirmgröße anzupassen
                #Nur zum anzeigen, sonst kann das raus
                img = cv2.resize(img,(1080,1920))

                # Zeige das Bild in einem Fenster an
                cv2.imshow('Original Bild', img)
                #Zeige Maske:
                cv2.imshow('Maske', mask)
                
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

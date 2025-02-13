import cv2
import FarbScanMethoden as fsm

#Testklasse, wenn IDS-Kamera nicht verfuegbar

def list_available_cameras():
            available_cameras = []
            for camera_id in range(10):
                print(f"Versuche Zugriff auf Kamera Nr. {camera_id} ...", end=" ")
                cap = cv2.VideoCapture(camera_id)
                if cap.isOpened():
                    print("ERFOLG!")
                    available_cameras.append(camera_id)
                    cap.release()
                else:
                    print("FEHLGESCHLAGEN!")
            return available_cameras

#Teste welche Kameras ich habe:
available_cameras = list_available_cameras()
print("-" * 40)
print("Verfügbare Kameras:", available_cameras)
print("-" * 40 + "\n")

cap = cv2.VideoCapture(0)

try:   
    while True:

        ret, frame = cap.read()

        if not ret:
            break
        frame = cv2.flip(frame, 1)

        img, result = fsm.createRedMask(frame)

        contours, hierarchy, mask = fsm.createContours(frame)

        cv2.imshow('Original', img)   
        cv2.imshow('Maske', result) #ja, Result ist die Maske

        #cv2.imshow('maske:', mask)
        #cv2.imshow('Contours:', Contours)

        # q zum beenden
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Nach dem Beenden des Skripts die Webcam freigeben und Fenster schließen
    cv2.destroyAllWindows()
# imports
import cv2
import mediapipe as mp
from mediapipe.python.solutions import face_detection
from mediapipe.python.solutions import pose as mp_pose
import time

import requests
from tkinter import Tk
import keyboard

from http_commands import PtzCommands


prev_time = time.time()
def cameraselector(index):
    global cam
    global camera_ip
    global camera_source
    global controller
    if index == 1:
        camera_ip = "192.168.1.37"
        camera_source = 1
    if index == 2:
        camera_ip = "192.168.1.245"
        camera_source = 2
    # Setup Camara source
    cam = cv2.VideoCapture(camera_source)
    controller = PtzCommands(camera_ip)

cameraselector(2)


win = Tk()
screenwidth = win.winfo_screenwidth()
screenheith = win.winfo_screenheight()

linke_linie = 0.35
rechte_linie = 0.65

obere_linie = 0.2
untere_linie = 0.45

Xmittelpunkt = -20
Ymittelpunkt = -20
gesicht = 0
abstand = []
presed = False
# wird dazu nutzen um zu checken ob sich die kamara sich bewegt
bewegung = "stop"
verfolgung = True


# Farben

BLUE = (255,0,0)
WHITE = (255,255,255)
RED = (0,0,255)
YELLOW = (0,175,175)


def getXmittelpunkt(Xboxmin,boxwidth):
    Xmittelpunkt = int(((Xboxmin * image_width)+((boxwidth+Xboxmin) * image_width))/2)
    return Xmittelpunkt

def getYmittelpunkt(Yboxmin,boxheight):
    Ymittelpunkt = int((Yboxmin*image_height+(Yboxmin+boxheight)*image_height)/2)
    return Ymittelpunkt

# functionen für das bewegen der kamara



# setup für die Gesichtserkennung
mpFaceDetection = mp.solutions.face_detection
mpPose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5,model_complexity=0)
pressed = False
face_detection = mpFaceDetection.FaceDetection(model_selection=1,min_detection_confidence=0.5)
cv2.namedWindow("Gesichtsverfolgung")

def keyboardevents():
    if keyboard.is_pressed('f'):
        if presed == False:
            verfolgung = not verfolgung

            presed = True
    else: presed = False
    if keyboard.is_pressed("1"):
        cameraselector(1)
    if keyboard.is_pressed("2"):
        cameraselector(2)

while True:
    success, frame = cam.read()
    if not success:
        print("skiped frame")
        continue

    frame = cv2.resize(frame,[1120,630])
    
    image_height, image_width, ic = frame.shape
    
    top_line = obere_linie * image_height
    bottom_line = untere_linie * image_height

    left_line = linke_linie * image_width
    right_line = rechte_linie * image_width

    x_mitte_box = int((left_line+right_line)/2)
    y_mitte_box = int((top_line+bottom_line)/2)


    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frameRGB = cv2.resize(frameRGB,(140, 80))
    frameGRAY = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = mpPose.process(frameRGB)
    if results.pose_landmarks:
        # Draw pose landmarks
        l = 0
        for landmark in results.pose_landmarks.landmark:
            x = int(landmark.x * image_width)
            y = int(landmark.y * image_height)
            if l == 0:
                cv2.circle(frame, (x, y), 5, RED, -1)
            else:
                cv2.circle(frame, (x, y), 5, BLUE, -1)

            l += 1

    keyboardevents()

# vierecke um die gesichter zeichnen und hilfslinien sowie text und fenster verkleinern falls zu groß
    

    cv2.imshow('Gesichtsverfolgung', frame)


    cv2.putText(frame, '[ESC] zum beenden', (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 1)

    cv2.putText(frame, '[f]wird vefolgt' if verfolgung else '[f]wird nicht verfolgt', (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, RED if verfolgung else WHITE, 1)   
    # Linien auf dem bildschirm zeichnen

    # linke linie
    cv2.line(frame, (int(left_line), 0),
             (int(left_line), image_height), WHITE, 2)
    # rechte linie
    cv2.line(frame, (int(right_line), 0),
             (int(right_line), image_height), WHITE, 2)
    # obere linie
    cv2.line(frame,(0,int(top_line)),
            (image_width,int(top_line)),WHITE,2)
    #untere linie
    cv2.line(frame,(0,int(bottom_line)),
            (image_width,int(bottom_line)),WHITE,2)
    
    curr_time = time.time()
    fps = int(1 / (curr_time - prev_time))
    prev_time = curr_time

    cv2.putText(frame, f'FPS: {fps}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


    cv2.imshow('Gesichtsverfolgung', frame)

# wenn es keine oder mehr als ein gesicht sieht dann bewegt es sich nicht
    if verfolgung == False and bewegung != "stop":
        bewegung = "stop"
        PtzCommands.stop()
        if verfolgung == False:
            pass
    if verfolgung == True and results.pose_landmarks:
        if verfolgung == True:
            Xmittelpunkt = results.pose_landmarks.landmark[0].x* image_width
            Ymittelpunkt = results.pose_landmarks.landmark[0].y* image_height
            # Bewegungen:

            # Diagonale bewegung

            if Xmittelpunkt < left_line and Ymittelpunkt < top_line and bewegung != "rechtsunten":
                controller.rechtsunten(1)
                bewegung = "rechtsunten"
            if Xmittelpunkt > right_line and Ymittelpunkt < top_line and bewegung != "linksunten":
                controller.linksunten(1)
                bewegung = "linksunten"
            if Xmittelpunkt < left_line and Ymittelpunkt > bottom_line and bewegung != "rechtsoben":
                controller.rechtsoben(1)
                bewegung = "rechtsoben"
            if Xmittelpunkt > right_line and Ymittelpunkt > bottom_line and bewegung != "linksoben":
                controller.linksoben(1)
                bewegung = "linksoben"


            # Horizontale bewegung

            if Xmittelpunkt < left_line and Ymittelpunkt > top_line and Ymittelpunkt < bottom_line and bewegung != "rechts":
                controller.rechts(1)
                bewegung = "rechts"
            if Xmittelpunkt > right_line and Ymittelpunkt > top_line and Ymittelpunkt < bottom_line and bewegung != "links":
                controller.links(1)
                bewegung = "links"


            # Vertikale bewegung

            if Ymittelpunkt < top_line and Xmittelpunkt > left_line and Xmittelpunkt < right_line and bewegung != "unten":
                controller.unten(1)
                bewegung = "unten"
            if Ymittelpunkt > bottom_line and Xmittelpunkt > left_line and Xmittelpunkt < right_line and bewegung != "oben":
                controller.oben(1)
                bewegung = "oben"

            # Stop

            if Xmittelpunkt > left_line and Xmittelpunkt < right_line and Ymittelpunkt > top_line and Ymittelpunkt < bottom_line and bewegung !="stop":
                    controller.stop()
                    bewegung = "stop"
        cv2.imshow('Gesichtsverfolgung', frame)

# alle 10ms bild refreshen [ESC] drücken um auszuschalten
    key = cv2.waitKey(1)
    if cv2.getWindowProperty("Gesichtsverfolgung", cv2.WND_PROP_VISIBLE) < 1 or key == 27:
        controller.stop()
        cam.release()
        cv2.destroyAllWindows()
        break

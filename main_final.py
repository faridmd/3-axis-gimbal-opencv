import cv2
import time
import pyfirmata
from math import atan2, degrees

# load haarcascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# init camera bawaan
# cap = cv2.VideoCapture(0)

# camera external
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

# init posisi servo
iterasi_x, iterasi_y = 90, 66

# ambil dimensi frame
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f'Height: {height}, Width: {width}')

# init arduino
board = pyfirmata.Arduino('COM6')
iter8 = pyfirmata.util.Iterator(board)
iter8.start()

# set pin untuk output
pin2 = board.get_pin('d:2:s')  # sumbu y
pin3 = board.get_pin('d:3:s')  # tilting
pin4 = board.get_pin('d:4:s')  # sumbu x

def move_servo(pin, angle):
    pin.write(angle)

# atur servo ke posisi awal
move_servo(pin2, 66)
move_servo(pin3, 90)
move_servo(pin4, 90)

def move(center, pos):
    delta = (pos - center) / 10
    if abs(delta) < 5:
        return 0
    return -1 if delta < 0 else 1

def on_change(value):
    print(value)
    flip_value=180-value
    move_servo(pin3, int(flip_value))

# bikin slider
cv2.namedWindow('Face Tracking')
cv2.createTrackbar('Tilting', 'Face Tracking', 90, 135, on_change)
cv2.setTrackbarMin('Tilting', 'Face Tracking', 45)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame.")
        break

    # flip camera biar ngga kebalik
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detek wajah
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # draw rectangle di face yang terdeteksi
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # hitung titik tengah
        center_x, center_y = x + w // 2, y + h // 2
        # cv2.circle(frame, (center_x, center_y), 2, (255, 255, 0), 1)

        # logic buat servo x
        movex = move(width / 2, center_x)
        iterasi_x += movex * 2
        move_servo(pin4, iterasi_x)

        # logic buat servo y
        movey = move(height / 2, center_y)
        iterasi_y += movey * 2
        move_servo(pin2, iterasi_y)

    cv2.putText(frame, f'Servo X: {iterasi_x}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, f'Servo Y: {iterasi_y}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # show frame
    cv2.imshow('Face Tracking', frame)

    # exit on pressing 'Esc'
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
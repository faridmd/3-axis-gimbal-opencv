import cv2 
import time
from math import atan2, degrees

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml') 

cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

#init sumbu
sumbu_x = 0
sumbu_y = 0
servo_x = 0
servo_y = 0

width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  
print('height :', height)
print('width :', width)


def move_x(center, pos):
    print(center, pos)
    if pos < center:
        print('kurang dari')
        selisih = -((center - pos) / 10)
        print(selisih)
        move = -1
        if selisih > -5:
            move = 0
    elif pos > center:
        print('lebih dari')
        selisih = abs(pos - center) / 10
        print(selisih)
        move = 1
        if selisih < 5:
            move = 0
    else:
        move = 0
    return move

while True: 
    ret, img = cap.read() 

    # flip frame
    img = cv2.flip(img, 1)

    # convert to gray scale of each frames
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detects faces of different sizes in the input image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # reset sumbu apabila tidak ada wajah
    if len(faces) == 0:
        # print(f'{time.time()} wajah tidak ada')
        sumbu_x = 0
        sumbu_y = 0
        servo_x = 0
        servo_y = 0

    for (x,y,w,h) in faces:
        # draw rectangle
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

        # detects eyes of different sizes in the input image
        eyes = eye_cascade.detectMultiScale(roi_gray) 

        # draw a rectangle in eyes
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,127,255),2)

         # if two eyes are detected, calculate the angle
        if len(eyes) >= 2:
            # cari titik tengah
            eye1 = eyes[0]
            eye2 = eyes[1]

            center1_x = eye1[0] + eye1[2] // 2
            center1_y = eye1[1] + eye1[3] // 2
            center2_x = eye2[0] + eye2[2] // 2
            center2_y = eye2[1] + eye2[3] // 2

            # draw circle tiap mata
            cv2.circle(roi_color, (center1_x, center1_y), 5, (255, 0, 0), -1)
            cv2.circle(roi_color, (center2_x, center2_y), 5, (255, 0, 0), -1)

            # hitung derajat
            delta_x = center2_x - center1_x
            delta_y = center2_y - center1_y
            angle_radians = atan2(delta_y, delta_x)
            angle_degrees = degrees(angle_radians)
            cv2.putText(img, f'Angle: {angle_degrees:.2f} deg', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


        # cari titik tengah rect
        center_x = x + w // 2
        center_y = y + h // 2

        # draw circle tengah
        cv2.circle(img, (center_x, center_y), 2, (255,255,0), 1 )

        sumbu_x = center_x
        sumbu_y = center_y

        servo_x = int(sumbu_x * 0.375)
        servo_y = int(sumbu_y * 0.28125)

        # print(f'{time.time()} wajah ada')
        print(move_x(width / 2, sumbu_x))

    # Print sumbu
    cv2.putText(img, f'sumbu x : {sumbu_x}', (12,30), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2) 
    cv2.putText(img, f'sumbu y : {sumbu_y}', (12,60), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2) 

    # Print servo
    cv2.putText(img, f'servo x : {servo_x}', (12,90), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2) 
    cv2.putText(img, f'servo y : {servo_y}', (12,120), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2) 
    cv2.circle(img, (0, 0), 10, (255, 0, 0), -1)  # Blue marker at (0,0)

    cv2.imshow('img',img)

    # Wait for Esc key to stop
    k = cv2.waitKey(1) & 0xff
    if k == 27:
        break

# Close the window
cap.release()

# De-allocate any associated memory usage
cv2.destroyAllWindows()
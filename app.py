import cv2
from modules.face_landmarks import FaceLandmarks

# To capture video from webcam.
cap = cv2.VideoCapture(0)  # To use a video file as input: cv2.VideoCapture('filename.mp4')
face_landmarks = FaceLandmarks()

while True:
    # Read the frame
    _, frame = cap.read()

    img = face_landmarks.detect(frame)
    cv2.imshow('img', img)
    # Stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
# Release the VideoCapture object
cap.release()

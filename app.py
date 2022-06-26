from modules.face_landmarks import FaceLandmarks
from modules.hand_landmarks import HandLandmarks
import cv2


# To capture video from webcam.
cap = cv2.VideoCapture(0)  # To use a video file as input: cv2.VideoCapture('filename.mp4')
face_landmarks = FaceLandmarks()
hand_landmarks = HandLandmarks()

while cap.isOpened():
    # Read the frame
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue
    frame = cv2.flip(frame, 1)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    hand_detected_frame = hand_landmarks.detect(frame, True)
    hand_face_detected_frame = face_landmarks.detect(gray_frame, hand_detected_frame)
    cv2.imshow('img', hand_face_detected_frame)
    # Stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
# Release the VideoCapture object
cap.release()
import cv2
import config
from modules.hand_landmarks import HandLandmark
from modules.face_detection import FaceDetection

cap = cv2.VideoCapture(1)  # To use a video file as input: cv2.VideoCapture('filename.mp4')
cap.set(3, config.camera['width'])
cap.set(4, config.camera['height'])

face_detection = FaceDetection()
hand_landmarks = HandLandmark()

while cap.isOpened():
    # Read the frame
    success, frame = cap.read()

    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

    face_detected_frame = face_detection.detect(cv2.flip(frame, 1))
    hand_face_detected_frame = hand_landmarks.detect(face_detected_frame, True)

    cv2.imshow('img', hand_face_detected_frame)
    # Stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
# Release the VideoCapture object
cap.release()

import cv2
from modules.face_landmarks import FaceLandmarks
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# To capture video from webcam.
cap = cv2.VideoCapture(0)  # To use a video file as input: cv2.VideoCapture('filename.mp4')
face_landmarks = FaceLandmarks()
# For webcam input:
# min_tracking_confidence=0.5
# min_detection_confidence=0.5
with mp_hands.Hands(model_complexity=0) as hands:
    while cap.isOpened():
        # Read the frame
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)

        # Draw the hand annotations on the image.
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        # Flip the image horizontally for a selfie-view display.

        img = face_landmarks.detect(frame)
        cv2.imshow('img', cv2.flip(img, 1))
        # Stop if escape key is pressed
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    # Release the VideoCapture object
cap.release()
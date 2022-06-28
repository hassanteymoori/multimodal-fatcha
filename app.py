import cv2
from modules.hand_landmarks import HandLandmark
from modules.face_mesh import FaceMesh
from modules.gesture.keypoint_classifier import KeyPointClassifier

cap = cv2.VideoCapture(0)  # To use a video file as input: cv2.VideoCapture('filename.mp4')

face_mesh = FaceMesh()
hand_landmarks = HandLandmark()
key_points_classifier = KeyPointClassifier()

while cap.isOpened():
    # Read the frame
    success, frame = cap.read()

    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

    face_detected_frame, head_pose_class = face_mesh.detect(
        cv2.flip(frame, 1),
        with_pose_estimator=True
    )
    hand_face_detected_frame, results, hand_class_label = hand_landmarks.detect(
        face_detected_frame,
        draw_bbox=False,
        landmarks=True
    )
    hand_face_gesture_frame, gesture_class_id = key_points_classifier.show_on_screen(
        hand_face_detected_frame,
        results
    )

    cv2.imshow('img', hand_face_gesture_frame)
    # Stop if escape key is pressed
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
# Release the VideoCapture object
cap.release()


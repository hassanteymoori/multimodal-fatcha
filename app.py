import cv2
import config
from modules.hand_landmarks import HandLandmark
from modules.face_mesh import FaceMesh
from modules.gesture.keypoint_classifier import KeyPointClassifier
from modules.anti_spoofing.challenge.response import ChallengeResponse

cap = cv2.VideoCapture(0)  # To use a video file as input: cv2.VideoCapture("filename.mp4")

face_mesh = FaceMesh()
hand_landmarks = HandLandmark()
key_points_classifier = KeyPointClassifier()
challenge = ChallengeResponse(config.challenge['number_of_challenges'])

while cap.isOpened():
    # Read the frame
    success, frame = cap.read()

    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use "break" instead of "continue".
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
    cv2.line(hand_face_gesture_frame, (10, 110), (500, 110), color=(168, 144, 34), thickness=2)

    # Stop if escape key is pressed
    key = cv2.waitKey(30) & 0xff
    if key == 27:
        break
    if key == 115:  # s --> start challenge response
        challenge.start_challenge()

    challenge.press_to_start_challenge_text(hand_face_gesture_frame)
    challenge.challenge_in_progress(
        hand_face_gesture_frame,
        {
            "head_pose_class": head_pose_class,
            "hand_class_label": hand_class_label,
            "gesture_class_id": gesture_class_id
        }
    )

    challenge.challenge_results(hand_face_gesture_frame)

    cv2.imshow("img", cv2.resize(hand_face_gesture_frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))

cap.release()

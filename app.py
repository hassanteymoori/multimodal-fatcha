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
    if not challenge.challenge_started and not challenge.challenge_result:
        challenge.add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text='PRESS `s` to start the challenge',
            given_location=(10, 140),
            given_color=(176, 119, 49)
        )
    interaction_data = {
        "head_pose_class": head_pose_class,
        "hand_class_label": hand_class_label,
        "gesture_class_id": gesture_class_id
    }

    # Stop if escape key is pressed
    key = cv2.waitKey(30) & 0xff
    if key == 27:
        break
    if key == 115:  # s --> start challenge response
        challenge.start_challenge()

    if challenge.challenge_started and challenge.total_attempt != config.challenge['allowed_attempt']:
        question = challenge.questions[challenge.current_question]
        challenge.add_timer(hand_face_gesture_frame)
        challenge.challenge_text[challenge.current_question] = question['text']
        current_result = challenge.challenge_case(question['id'], interaction_data)
        if question['type'] == 1:
            challenge.add_icon(hand_face_gesture_frame, question["link"])
        challenge.next_consecutive(question, current_result)

        for index, text in enumerate(challenge.challenge_text):
            challenge.base_location_height = 180 + index * 30
            challenge.add_text_to_frame(
                given_frame=hand_face_gesture_frame,
                given_text=text,
                given_location=(10, challenge.base_location_height),
                given_color=(150, 47, 140)
            )
    if challenge.challenge_result:
        cv2.line(hand_face_gesture_frame, (10, challenge.base_location_height + 25), (500, challenge.base_location_height + 25),
                 color=(0, 255, 0), thickness=1)
        challenge.add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text='Access Granted Successfully',
            given_location=(10, challenge.base_location_height + 50),
            given_color=(0, 255, 0)
        )
    if challenge.total_attempt != 0 and (challenge.total_attempt < config.challenge['allowed_attempt']):
        desc = 'Total attempt:  ' + str(challenge.total_attempt)
        desc += '| You can try ' + str(config.challenge["allowed_attempt"] - challenge.total_attempt) + ' more times'
        challenge.add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text=desc,
            given_location=(10, 90),
            given_color=(0, 0, 255)
        )

    if not challenge.challenge_result and challenge.total_attempt == config.challenge['allowed_attempt']:
        cv2.line(hand_face_gesture_frame, (10, challenge.base_location_height + 25), (500, challenge.base_location_height + 25),
                 color=(0, 0, 255), thickness=2)
        challenge.add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text='Access Denied',
            given_location=(10, challenge.base_location_height + 50),
            given_color=(0, 0, 255)
        )

    cv2.imshow("img", cv2.resize(hand_face_gesture_frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))

cap.release()

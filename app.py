import cv2
import numpy as np
import time

import config
from modules.hand_landmarks import HandLandmark
from modules.face_mesh import FaceMesh
from modules.gesture.keypoint_classifier import KeyPointClassifier
from modules.anti_spoofing.challenge.response import ChallengeResponse

cap = cv2.VideoCapture(0)  # To use a video file as input: cv2.VideoCapture("filename.mp4")

face_mesh = FaceMesh()
hand_landmarks = HandLandmark()
key_points_classifier = KeyPointClassifier()

flag_start_challenge = False
challenge = ChallengeResponse()
questions = challenge.random_questions(config.challenge['number_of_challenges'])
starter_text = 'press `s` when you were ready to start the challenge'
number_of_question = len(questions)
response = np.zeros(number_of_question)
current_question = 0
start_time = 0
timer = config.challenge['time_per_question']
total_result_for_each_question = []
challenge_result = 'Failed'
challenge_text = ['' for i in range(number_of_question)]
height = 150


def show_image(img, text, color=(0, 0, 0), height=150):
    cv2.putText(
        img,
        text,
        (10, height),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        color,
        2)
    return img


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

    cv2.line(hand_face_gesture_frame, (10, 80), (500, 80), color=(168, 144, 34), thickness=1)
    show_image(hand_face_gesture_frame, starter_text, color=(176, 119, 49),  height=110)
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
        flag_start_challenge = True
        starter_text = ''
        start_time = time.time()

    if flag_start_challenge:
        question = questions[current_question]
        challenge_text[current_question] = question['text']
        current_result = challenge.challenge_case(question['id'], interaction_data)
        print(current_result)
        if current_result:
            challenge_text[current_question] = f'{question["text"]} :detected! keep it'
            total_result_for_each_question.append(current_result)
            if len(total_result_for_each_question) >= config.challenge['consecutive']:
                if current_question == (number_of_question - 1):
                    challenge_result = 'Passed'
                    flag_start_challenge = False

                challenge_text[current_question] = f'{question["text"]} :passed!'
                current_question += 1
        else:
            total_result_for_each_question = []

    for index, text in enumerate(challenge_text):
        height = 150 + index * 30

        show_image(hand_face_gesture_frame, text, color=(150, 47, 140), height=height)
    if challenge_result == 'Passed':
        show_image(hand_face_gesture_frame, color=(0, 255, 0), text='Access Granted Successfully', height=height + 50)

    cv2.imshow("img", cv2.resize(hand_face_gesture_frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))

cap.release()

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
challenge = ChallengeResponse()
questions = challenge.random_questions(config.challenge['number_of_challenges'])

flag_to_start_the_challenge = False
current_question = 0
n_consecutive_frames = 0
challenge_text = ['' for i in range(len(questions))]
challenge_result = False

base_location_height = 150


def start_challenge():
    global current_question, questions, challenge_result, \
        flag_to_start_the_challenge, n_consecutive_frames, challenge_text, base_location_height
    flag_to_start_the_challenge = True
    current_question = 0
    n_consecutive_frames = 0
    challenge_result = False
    challenge_text = ['' for i in range(len(questions))]
    base_location_height = 150


def add_text_to_frame(given_frame, given_text, given_location=(10, 150), given_color=(0, 0, 0)):
    cv2.putText(
        img=given_frame,
        text=given_text,
        org=given_location,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.75,
        color=given_color,
        thickness=2
    )

    return given_frame


def next_question():
    global current_question, questions, challenge_result, \
        flag_to_start_the_challenge, n_consecutive_frames, challenge_text

    if current_question == (len(questions) - 1):
        challenge_result = True
        flag_to_start_the_challenge = False

    challenge_text[current_question] = f'{question["text"]} :passed!'
    n_consecutive_frames = 0
    current_question += 1

    return


def next_consecutive(current_question_obj, challenge_current_result):
    global current_question, n_consecutive_frames, challenge_text
    if challenge_current_result:
        challenge_text[current_question] = f'{current_question_obj["text"]} :detected! keep it'
        n_consecutive_frames += 1
        if n_consecutive_frames >= config.challenge['consecutive']:
            next_question()
    else:
        n_consecutive_frames = 0

    return


def add_icon(to_frame, path_to_icon):
    emoji = cv2.imread(path_to_icon)
    hs, ws, _ = emoji.shape
    h, w, _ = to_frame.shape
    to_frame[0:hs, w - ws:w] = emoji
    return to_frame


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
    if not flag_to_start_the_challenge and not challenge_result:
        add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text='PRESS `s` to start the challenge',
            given_location=(10, 110),
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
        start_challenge()

    if flag_to_start_the_challenge:
        question = questions[current_question]
        challenge_text[current_question] = question['text']
        current_result = challenge.challenge_case(question['id'], interaction_data)
        if question['type'] == 1:
            add_icon(hand_face_gesture_frame, question["link"])
        next_consecutive(question, current_result)

    for index, text in enumerate(challenge_text):
        base_location_height = 150 + index * 30
        add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text=text,
            given_location=(10, base_location_height),
            given_color=(150, 47, 140)
        )
    if challenge_result:
        cv2.line(hand_face_gesture_frame, (10, base_location_height + 25), (500, base_location_height + 25), color=(0, 255, 0), thickness=1)
        add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text='Access Granted Successfully',
            given_location=(10, base_location_height + 50),
            given_color=(0, 255, 0)
        )

    cv2.imshow("img", cv2.resize(hand_face_gesture_frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))

cap.release()

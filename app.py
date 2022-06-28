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

starter_text = 'press `s` when you were ready to start the challenge'

challenge_result = 'Failed'
challenge_text = ['' for i in range(len(questions))]
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


def next_question():
    global current_question, questions, challenge_result, \
        flag_to_start_the_challenge, n_consecutive_frames, challenge_text

    if current_question == (len(questions) - 1):
        challenge_result = 'Passed'
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


def add_icon(frame, path_to_icon):
    emoji = cv2.imread(path_to_icon)
    hs, ws, _ = emoji.shape
    h, w, _ = frame.shape
    frame[0:hs, w - ws:w] = emoji
    return frame


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
    show_image(hand_face_gesture_frame, starter_text, color=(176, 119, 49), height=110)
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
        flag_to_start_the_challenge = True
        starter_text = ''

    if flag_to_start_the_challenge:
        question = questions[current_question]
        challenge_text[current_question] = question['text']
        current_result = challenge.challenge_case(question['id'], interaction_data)
        if question['type'] == 1:
            add_icon(hand_face_gesture_frame, question["link"])
        next_consecutive(question, current_result)

    for index, text in enumerate(challenge_text):
        height = 150 + index * 30

        show_image(hand_face_gesture_frame, text, color=(150, 47, 140), height=height)
    if challenge_result == 'Passed':
        show_image(hand_face_gesture_frame, color=(0, 255, 0), text='Access Granted Successfully', height=height + 50)

    cv2.imshow("img", cv2.resize(hand_face_gesture_frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))

cap.release()

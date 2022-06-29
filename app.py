import cv2
import config
import time
from modules.hand_landmarks import HandLandmark
from modules.face_mesh import FaceMesh
from modules.gesture.keypoint_classifier import KeyPointClassifier
from modules.anti_spoofing.challenge.response import ChallengeResponse

cap = cv2.VideoCapture(0)  # To use a video file as input: cv2.VideoCapture("filename.mp4")

face_mesh = FaceMesh()
hand_landmarks = HandLandmark()
key_points_classifier = KeyPointClassifier()
challenge = ChallengeResponse(config.challenge['number_of_challenges'])

base_location_height = 170

current_time = 0
time_per_question = 0
timer_blinking = True


def reset_time_per_question():
    global time_per_question, current_time
    current_time = time.time()
    time_per_question = current_time + config.challenge['time_per_question']


def start_challenge():
    global challenge, \
        base_location_height, current_time, time_per_question
    challenge.challenge_started = True
    challenge.current_question = 0
    challenge.n_consecutive_frames = 0
    challenge.challenge_result = False
    challenge.challenge_text = ['' for i in range(challenge.number_of_questions)]
    base_location_height = 180
    reset_time_per_question()


def add_text_to_frame(given_frame, given_text, given_location=(10, 150), given_color=(0, 0, 0), font_scale=0.75):
    cv2.putText(
        img=given_frame,
        text=given_text,
        org=given_location,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=font_scale,
        color=given_color,
        thickness=2
    )


def next_question():
    global  challenge

    if challenge.current_question == (challenge.number_of_questions - 1):
        challenge.challenge_result = True
        challenge.challenge_started = False

    challenge.challenge_text[challenge.current_question] = f'{question["text"]} :passed!'
    challenge.n_consecutive_frames = 0
    challenge.current_question += 1

    reset_time_per_question()
    return


def next_consecutive(current_question_obj, challenge_current_result):
    global challenge
    if challenge_current_result:
        challenge.challenge_text[challenge.current_question] = f'{current_question_obj["text"]} :detected! keep it'
        challenge.n_consecutive_frames += 1
        if challenge.n_consecutive_frames >= config.challenge['consecutive']:
            next_question()
    else:
        challenge.n_consecutive_frames = 0

    return


def add_icon(to_frame, path_to_icon):
    emoji = cv2.imread(path_to_icon)
    hs, ws, _ = emoji.shape
    h, w, _ = to_frame.shape
    to_frame[0:hs, w - ws:w] = emoji
    return to_frame


def challenge_failed():
    global challenge, \
        base_location_height

    challenge.sample_again()
    challenge.current_question = 0
    challenge.n_consecutive_frames = 0
    challenge.challenge_text = ['' for i in range(challenge.number_of_questions)]
    challenge.challenge_result = False
    base_location_height = 180
    reset_time_per_question()
    challenge.total_attempt += 1


def add_timer(to_frame):
    global current_time, time_per_question, timer_blinking
    timer = int(time_per_question - time.time())
    if timer >= 0:
        rec_width, rec_height = 220, 55
        x1, y1 = int(to_frame.shape[1] // 2) - int(rec_width / 2), 0
        if timer < (config.challenge['time_per_question'] // 2):
            timer_blinking = not timer_blinking
        if timer_blinking:
            cv2.rectangle(
                to_frame,
                (x1, y1),
                (x1 + rec_width, y1 + rec_height),
                (143, 138, 127),
                -1)
            add_text_to_frame(
                given_frame=to_frame,
                given_text='Time left: ' + str(int(time_per_question - time.time())),
                given_location=(x1 + 5, 40),
                # given_color=(3, 186, 252),
                given_color=(230, 230, 230),
                font_scale=1.1,
            )
    else:
        challenge_failed()


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
        add_text_to_frame(
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
        start_challenge()

    if challenge.challenge_started and challenge.total_attempt != config.challenge['allowed_attempt']:
        question = challenge.questions[challenge.current_question]
        add_timer(hand_face_gesture_frame)
        challenge.challenge_text[challenge.current_question] = question['text']
        current_result = challenge.challenge_case(question['id'], interaction_data)
        if question['type'] == 1:
            add_icon(hand_face_gesture_frame, question["link"])
        next_consecutive(question, current_result)

        for index, text in enumerate(challenge.challenge_text):
            base_location_height = 180 + index * 30
            add_text_to_frame(
                given_frame=hand_face_gesture_frame,
                given_text=text,
                given_location=(10, base_location_height),
                given_color=(150, 47, 140)
            )
    if challenge.challenge_result:
        cv2.line(hand_face_gesture_frame, (10, base_location_height + 25), (500, base_location_height + 25),
                 color=(0, 255, 0), thickness=1)
        add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text='Access Granted Successfully',
            given_location=(10, base_location_height + 50),
            given_color=(0, 255, 0)
        )
    if challenge.total_attempt != 0 and (challenge.total_attempt < config.challenge['allowed_attempt']):
        desc = 'Total attempt:  ' + str(challenge.total_attempt)
        desc += '| You can try ' + str(config.challenge["allowed_attempt"] - challenge.total_attempt) + ' more times'
        add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text=desc,
            given_location=(10, 90),
            given_color=(0, 0, 255)
        )

    if not challenge.challenge_result and challenge.total_attempt == config.challenge['allowed_attempt']:
        cv2.line(hand_face_gesture_frame, (10, base_location_height + 25), (500, base_location_height + 25),
                 color=(0, 0, 255), thickness=2)
        add_text_to_frame(
            given_frame=hand_face_gesture_frame,
            given_text='Access Denied',
            given_location=(10, base_location_height + 50),
            given_color=(0, 0, 255)
        )

    cv2.imshow("img", cv2.resize(hand_face_gesture_frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC))

cap.release()

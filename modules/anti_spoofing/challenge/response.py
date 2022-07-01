import os
import time
import random
import sys
import config
import cv2
sys.path.append('../../../')

root_dir = os.path.dirname(__file__)
emoji_directory = os.path.join(root_dir, "emoji")


class ChallengeResponse:

    def __init__(self, number_of_questions=10):
        self.challenge_started = False
        self.current_question = 0
        self.number_of_questions = number_of_questions
        self.questions = self._random_questions(number_of_questions)
        self.challenge_result = False
        self.n_consecutive_frames = 0
        self.text = ''
        self.detected = False
        self.total_attempt = 0
        self.total_attempt_text = ''
        self.base_location_height = 180
        self.current_time = 0
        self.time_per_question = 0
        self.timer_blinking = True

    def is_challenge_in_progress(self):
        return self.challenge_started and self.total_attempt <= config.challenge['allowed_attempt']

    def challenge_in_progress(self, frame, interaction_data):
        if self.is_challenge_in_progress():
            question = self.questions[self.current_question]
            self.add_timer(frame)
            self.text = question['text']
            self.detected = False
            current_result = self.challenge_case(question['id'], interaction_data)
            self.next_consecutive(question, current_result)

    def challenge_results(self, frame):

        if self.total_attempt != 0 and (self.total_attempt <= config.challenge['allowed_attempt']):
            desc = 'Total attempt: ' + str(self.total_attempt)

            if self.total_attempt == 3:
                desc += ' | LAST CHANCE!'
            else:
                desc += ' | You can try ' + str(
                    config.challenge["allowed_attempt"] - self.total_attempt) + ' more times'
            self.add_text_to_frame(
                given_frame=frame,
                given_text=desc,
                given_location=(10, 90),
                given_color=(0, 0, 255)
            )

    def is_on_going(self):
        on_going = self.total_attempt != 0 and (self.total_attempt <= config.challenge['allowed_attempt'])
        if on_going:
            self.total_attempt_text = 'Total attempt: ' + str(self.total_attempt)

            if self.total_attempt == 3:
                self.total_attempt_text += ' | LAST CHANCE!'
            else:
                self.total_attempt_text += ' | You can try '
                self.total_attempt_text += str(config.challenge["allowed_attempt"] - self.total_attempt)
                self.total_attempt_text += ' more times!'
            return on_going

    def is_access_granted(self):
        return self.challenge_result

    def is_access_denied(self):
        return not self.challenge_result and self.total_attempt > config.challenge['allowed_attempt']

    def start_challenge(self):
        self.challenge_started = True
        self.current_question = 0
        self.n_consecutive_frames = 0
        self.challenge_result = False
        self.detected = False
        self.text = ''
        self.base_location_height = 180
        self.reset_time_per_question()
        self.total_attempt += 1

    def challenge_failed(self):
        self.sample_again()
        self.start_challenge()

    def reset_time_per_question(self):
        self.current_time = time.time()
        self.time_per_question = self.current_time + config.challenge['time_per_question']

    def next_consecutive(self, question, current_result):
        if current_result:
            self.detected = True
            self.text = f'{question["text"]} :detected! keep it'
            self.n_consecutive_frames += 1
            if self.n_consecutive_frames >= config.challenge['consecutive']:
                self.next_question()
        else:
            self.n_consecutive_frames = 0
        return

    def next_question(self):

        if self.current_question == (self.number_of_questions - 1):
            self.challenge_result = True
            self.challenge_started = False

        self.n_consecutive_frames = 0
        self.current_question += 1
        self.reset_time_per_question()

    @staticmethod
    def add_icon(to_frame, path_to_icon):
        emoji = cv2.imread(path_to_icon)
        hs, ws, _ = emoji.shape
        h, w, _ = to_frame.shape
        to_frame[0:hs, w - ws:w] = emoji
        return to_frame

    @staticmethod
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

    def add_timer(self, to_frame):
        timer = int(self.time_per_question - time.time())
        if timer >= 0:
            rec_width, rec_height = 220, 55
            x1, y1 = int(to_frame.shape[1] // 2) - int(rec_width / 2), 0
            if timer < (config.challenge['time_per_question'] // 2):
                self.timer_blinking = not self.timer_blinking
            if self.timer_blinking:
                cv2.rectangle(
                    to_frame,
                    (x1, y1),
                    (x1 + rec_width, y1 + rec_height),
                    (143, 138, 127),
                    -1)
                self.add_text_to_frame(
                    given_frame=to_frame,
                    given_text='Time left: ' + str(int(self.time_per_question - time.time())),
                    given_location=(x1 + 5, 40),
                    given_color=(230, 230, 230),
                    font_scale=1.1,
                )
        else:
            self.challenge_failed()

    def _random_questions(self, number):
        questions = self._questions()
        if number > len(questions):
            Exception('Number of the request sub sample are above the total number of the question')
        return random.sample(questions, number)

    def sample_again(self):
        self.questions = self._random_questions(self.number_of_questions)

    # ________________________ type 0 challenges _______________________ #
    @staticmethod
    def _challenge_right_hand(interaction_date):
        return True if interaction_date['hand_class_label'] == 'Right' else False

    @staticmethod
    def _challenge_left_land(interaction_date):
        return True if interaction_date['hand_class_label'] == 'Left' else False

    @staticmethod
    def _challenge_head_pose_left(interaction_date):
        return True if interaction_date['head_pose_class'] == 1 else False

    @staticmethod
    def _challenge_head_pose_right(interaction_date):
        return True if interaction_date['head_pose_class'] == 2 else False

    @staticmethod
    def _challenge_head_pose_up(interaction_date):
        return True if interaction_date['head_pose_class'] == 4 else False

    @staticmethod
    def _challenge_head_pose_forward(interaction_date):
        return True if interaction_date['head_pose_class'] == 5 else False

    # ________________________ type 1 challenges _______________________ #
    @staticmethod
    def _is_gesture_unknown(hand_class):
        if hand_class == 9:
            return True

    def _challenge_like_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 0 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_like_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 0 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_dislike_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 1 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_dislike_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 1 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_callme_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 2 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_callme_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 2 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_number_four_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 3 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_number_four_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 3 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_hi_five_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 4 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_hi_five_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 4 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_victory_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 5 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_victory_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 5 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_perfect_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 6 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_perfect_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 6 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_crossed_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 8 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_crossed_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 8 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    def _challenge_omg_with_right(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 7 and self._challenge_right_hand(interaction_date):
            return True
        else:
            return False

    def _challenge_omg_with_left(self, interaction_date):
        if self._is_gesture_unknown(interaction_date['gesture_class_id']):
            return False
        if interaction_date['gesture_class_id'] == 7 and self._challenge_left_land(interaction_date):
            return True
        else:
            return False

    @staticmethod
    def _challenge_emotion_angry(interaction_date):
        if interaction_date['emotion_class_id'] == 0:
            return True
        else:
            return False

    @staticmethod
    def _challenge_emotion_happy(interaction_date):
        if interaction_date['emotion_class_id'] == 3:
            return True
        else:
            return False

    @staticmethod
    def _challenge_emotion_neutral(interaction_date):
        if interaction_date['emotion_class_id'] == 4:
            return True
        else:
            return False

    @staticmethod
    def _challenge_emotion_surprise(interaction_date):
        if interaction_date['emotion_class_id'] == 6:
            return True
        else:
            return False


    def challenge_case(self, status, interaction_date):
        match status:
            case 1:
                return self._challenge_right_hand(interaction_date)
            case 2:
                return self._challenge_left_land(interaction_date)
            case 3:
                return self._challenge_head_pose_left(interaction_date)
            case 4:
                return self._challenge_head_pose_right(interaction_date)
            case 5:
                return self._challenge_head_pose_up(interaction_date)
            case 7:
                return self._challenge_head_pose_forward(interaction_date)
            case 8:
                return self._challenge_like_with_right(interaction_date)
            case 9:
                return self._challenge_like_with_left(interaction_date)
            case 10:
                return self._challenge_dislike_with_right(interaction_date)
            case 11:
                return self._challenge_dislike_with_left(interaction_date)
            case 12:
                return self._challenge_callme_with_right(interaction_date)
            case 13:
                return self._challenge_callme_with_left(interaction_date)
            case 14:
                return self._challenge_number_four_with_right(interaction_date)
            case 15:
                return self._challenge_number_four_with_left(interaction_date)
            case 16:
                return self._challenge_hi_five_with_right(interaction_date)
            case 17:
                return self._challenge_hi_five_with_left(interaction_date)
            case 18:
                return self._challenge_victory_with_right(interaction_date)
            case 19:
                return self._challenge_victory_with_left(interaction_date)
            case 20:
                return self._challenge_perfect_with_right(interaction_date)
            case 21:
                return self._challenge_perfect_with_left(interaction_date)
            case 22:
                return self._challenge_crossed_with_right(interaction_date)
            case 23:
                return self._challenge_crossed_with_left(interaction_date)
            case 24:
                return self._challenge_omg_with_right(interaction_date)
            case 25:
                return self._challenge_omg_with_left(interaction_date)
            case 26:
                return self._challenge_emotion_angry(interaction_date)
            case 27:
                return self._challenge_emotion_happy(interaction_date)
            case 28:
                return self._challenge_emotion_neutral(interaction_date)
            case 29:
                return self._challenge_emotion_surprise(interaction_date)
            case _:
                return False

    @staticmethod
    def _questions():
        return [
            {
                "id": 1,
                "type": 0,
                "text": "Show your RIGHT hand, please!"
            },
            {
                "id": 2,
                "type": 0,
                "text": "Show your LEFT hand, please!"
            },
            {
                "id": 3,
                "type": 0,
                "text": "Turn your head LEFT"},
            {
                "id": 4,
                "type": 0,
                "text": "Turn your head RIGHT"},
            {
                "id": 5,
                "type": 0,
                "text": "Turn your head UP"
            },

            {
                "id": 7,
                "type": 0,
                "text": "Keep your head Forward"},
            {
                "id": 8,
                "type": 1,
                "text": "Show me `Like` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "like.png")
            },
            {
                "id": 9,
                "type": 1,
                "text": "Show me `Like` with your LEFT hand",
                "link": os.path.join(emoji_directory, "like.png")
            },
            {
                "id": 10,
                "type": 1,
                "text": "Show me `Dislike` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "dislike.png")
            },
            {
                "id": 11,
                "type": 1,
                "text": "Show me `Dislike` with your LEFT hand",
                "link": os.path.join(emoji_directory, "dislike.png")
            },
            {
                "id": 12,
                "type": 1,
                "text": "Show me `Call me` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "call-me.png")
            },
            {
                "id": 13,
                "type": 1,
                "text": "Show me `Call me` with your LEFT hand",
                "link": os.path.join(emoji_directory, "call-me.png")
            },
            {
                "id": 14,
                "type": 1,
                "text": "Show me `Four` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "four.png")
            },
            {
                "id": 15,
                "type": 1,
                "text": "Show me `Four` with your LEFT hand",
                "link": os.path.join(emoji_directory, "four.png")
            },
            {
                "id": 16,
                "type": 1,
                "text": "Show me `Hi-five` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "hi_five.png")
            },
            {
                "id": 17,
                "type": 1,
                "text": "Show me `Hi-five` with your LEFT hand",
                "link": os.path.join(emoji_directory, "hi_five.png")
            },
            {
                "id": 18,
                "type": 1,
                "text": "Show me `Victory` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "victory.png")
            },
            {
                "id": 19,
                "type": 1,
                "text": "Show me `Victory` with your LEFT hand",
                "link": os.path.join(emoji_directory, "victory.png")
            },
            {
                "id": 20,
                "type": 1,
                "text": "Show me `Perfect` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "perfect.png")
            },
            {
                "id": 21,
                "type": 1,
                "text": "Show me `Perfect` with your LEFT hand",
                "link": os.path.join(emoji_directory, "perfect.png")
            },
            {
                "id": 22,
                "type": 1,
                "text": "Show me `Finger crossed` with your RIGHT hand",
                "link": os.path.join(emoji_directory, "crossed.png")
            },
            {
                "id": 23,
                "type": 1,
                "text": "Show me `Finger crossed` with your LEFT hand",
                "link": os.path.join(emoji_directory, "crossed.png")
            },
            # {
            #     "id": 24,
            #     "type": 1,
            #     "text": "Show me `Mamma Mia!` with your RIGHT hand",
            #     "link": os.path.join(emoji_directory, "omg.png")
            # },
            # {
            #     "id": 25,
            #     "type": 1,
            #     "text": "Show me `Mamma Mia!` with your LEFT hand",
            #     "link": os.path.join(emoji_directory, "omg.png")
            # },
            {
                "id": 26,
                "type": 1,
                "text": "Try to pretend that you are `Angry`",
                "link": os.path.join(emoji_directory, "angry.png")
            },
            {
                "id": 27,
                "type": 1,
                "text": "Try to pretend that you are `Happy`",
                "link": os.path.join(emoji_directory, "happy.png")
            },
            {
                "id": 28,
                "type": 1,
                "text": "Stay `Neutral` (you have no emotion)",
                "link": os.path.join(emoji_directory, "neutral.png")
            },
            {
                "id": 29,
                "type": 1,
                "text": "Try to pretend that you are `Surprised`",
                "link": os.path.join(emoji_directory, "surprised.png")
            },

        ]

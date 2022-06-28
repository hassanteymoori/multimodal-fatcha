import os
import random
root_dir = os.path.dirname(__file__)
emoji_directory = os.path.join(root_dir, "emoji")


class ChallengeResponse:
    def random_questions(self, number):
        questions = self.questions()
        if number > len(questions):
            Exception('Number of the request sub sample are above the total number of the question')
        return random.sample(questions, number)

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
            case _: return False

    @staticmethod
    def questions():
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
                "link": os.path.join(emoji_directory,"like.png")
            },
            {
                "id": 9,
                "type": 1,
                "text": "Show me `Like` with your LEFT hand",
                "link": os.path.join(emoji_directory,"like.png")
            },
            {
                "id": 10,
                "type": 1,
                "text": "Show me `Dislike` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"dislike.png")
            },
            {
                "id": 11,
                "type": 1,
                "text": "Show me `Dislike` with your LEFT hand",
                "link": os.path.join(emoji_directory,"dislike.png")
            },
            {
                "id": 12,
                "type": 1,
                "text": "Show me `Call me` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"call-me.png")
            },
            {
                "id": 13,
                "type": 1,
                "text": "Show me `Call me` with your LEFT hand",
                "link": os.path.join(emoji_directory,"call-me.png")
            },
            {
                "id": 14,
                "type": 1,
                "text": "Show me `Four` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"four.png")
            },
            {
                "id": 15,
                "type": 1,
                "text": "Show me `Four` with your LEFT hand",
                "link": os.path.join(emoji_directory,"four.png")
            },
            {
                "id": 16,
                "type": 1,
                "text": "Show me `Hi-five` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"hi_five.png")
            },
            {
                "id": 17,
                "type": 1,
                "text": "Show me `Hi-five` with your LEFT hand",
                "link": os.path.join(emoji_directory,"hi_five.png")
            },
            {
                "id": 18,
                "type": 1,
                "text": "Show me `Victory` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"victory.png")
            },
            {
                "id": 19,
                "type": 1,
                "text": "Show me `Victory` with your LEFT hand",
                "link": os.path.join(emoji_directory,"victory.png")
            },
            {
                "id": 20,
                "type": 1,
                "text": "Show me `Perfect` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"perfect.png")
            },
            {
                "id": 21,
                "type": 1,
                "text": "Show me `Perfect` with your LEFT hand",
                "link": os.path.join(emoji_directory,"perfect.png")
            },
            {
                "id": 22,
                "type": 1,
                "text": "Show me `Finger crossed` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"crossed.png")
            },
            {
                "id": 23,
                "type": 1,
                "text": "Show me `Finger crossed` with your LEFT hand",
                "link": os.path.join(emoji_directory,"crossed.png")
            },
            {
                "id": 24,
                "type": 1,
                "text": "Show me `Mamma Mia!` with your RIGHT hand",
                "link": os.path.join(emoji_directory,"omg.png")
            },
            {
                "id": 25,
                "type": 1,
                "text": "Show me `Mamma Mia!` with your LEFT hand",
                "link": os.path.join(emoji_directory,"omg.png")
            },

        ]

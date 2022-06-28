import os
import random


class ChallengeResponse:
    def random_questions(self, number):
        questions = self.questions()
        if number > len(questions):
            Exception('Number of the request sub sample are above the total number of the question')
        return random.sample(questions, number)

    @staticmethod
    def challenge_right_hand(interaction_date):
        return True if interaction_date['hand_class_label'] == 'Right' else False

    @staticmethod
    def challenge_left_land(interaction_date):
        return True if interaction_date['hand_class_label'] == 'Left' else False

    @staticmethod
    def challenge_head_pose_left(interaction_date):
        return True if interaction_date['head_pose_class'] == 1 else False

    @staticmethod
    def challenge_head_pose_right(interaction_date):
        return True if interaction_date['head_pose_class'] == 2 else False

    @staticmethod
    def challenge_head_pose_down(interaction_date):
        return True if interaction_date['head_pose_class'] == 3 else False

    @staticmethod
    def challenge_head_pose_up(interaction_date):
        return True if interaction_date['head_pose_class'] == 4 else False

    @staticmethod
    def challenge_head_pose_forward(interaction_date):
        return True if interaction_date['head_pose_class'] == 5 else False

    def challenge_case(self, status, interaction_date):
        match status:
            case 1: return self.challenge_right_hand(interaction_date)
            case 2: return self.challenge_left_land(interaction_date)
            case 3: return self.challenge_head_pose_left(interaction_date)
            case 4: return self.challenge_head_pose_right(interaction_date)
            case 5: return self.challenge_head_pose_up(interaction_date)
            case 6: return self.challenge_head_pose_down(interaction_date)
            case 7: return self.challenge_head_pose_forward(interaction_date)

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
                "text": "Turn your head UP"},
            {
                "id": 6,
                "type": 0,
                "text": "Turn your head DOWN"},
            {
                "id": 7,
                "type": 0,
                "text": "Keep your head Forward"},
            {
                "id": 8,
                "type": 1,
                "text": "Show me `Like` with your RIGHT hand",
                "link": os.path.join("emoji/like.png")
            },
            {
                "id": 9,
                "type": 1,
                "text": "Show me `Like` with your LEFT hand",
                "link": os.path.join("emoji/like.png")
            },
            {
                "id": 10,
                "type": 1,
                "text": "Show me `Dislike` with your RIGHT hand",
                "link": os.path.join("emoji/dislike.png")
            },
            {
                "id": 11,
                "type": 1,
                "text": "Show me `Dislike` with your LEFT hand",
                "link": os.path.join("emoji/dislike.png")
            },
            {
                "id": 12,
                "type": 1,
                "text": "Show me `Call me` with your RIGHT hand",
                "link": os.path.join("emoji/call-me.png")
            },
            {
                "id": 13,
                "type": 1,
                "text": "Show me `Call me` with your LEFT hand",
                "link": os.path.join("emoji/call-me.png")
            },
            {
                "id": 14,
                "type": 1,
                "text": "Show me `Four` with your RIGHT hand",
                "link": os.path.join("emoji/four.png")
            },
            {
                "id": 15,
                "type": 1,
                "text": "Show me `Four` with your LEFT hand",
                "link": os.path.join("emoji/four.png")
            },
            {
                "id": 16,
                "type": 1,
                "text": "Show me `Hi-five` with your RIGHT hand",
                "link": os.path.join("emoji/hi_five.png")
            },
            {
                "id": 17,
                "type": 1,
                "text": "Show me `Hi-five` with your LEFT hand",
                "link": os.path.join("emoji/hi_five.png")
            },
            {
                "id": 18,
                "type": 1,
                "text": "Show me `Victory` with your RIGHT hand",
                "link": os.path.join("emoji/victory.png")
            },
            {
                "id": 19,
                "type": 1,
                "text": "Show me `Victory` with your LEFT hand",
                "link": os.path.join("emoji/victory.png")
            },
            {
                "id": 20,
                "type": 1,
                "text": "Show me `Perfect` with your RIGHT hand",
                "link": os.path.join("emoji/perfect.png")
            },
            {
                "id": 21,
                "type": 1,
                "text": "Show me `Perfect` with your LEFT hand",
                "link": os.path.join("emoji/perfect.png")
            },
            {
                "id": 22,
                "type": 1,
                "text": "Show me `Finger crossed` with your RIGHT hand",
                "link": os.path.join("emoji/crossed.png")
            },
            {
                "id": 23,
                "type": 1,
                "text": "Show me `Finger crossed` with your LEFT hand",
                "link": os.path.join("emoji/crossed.png")
            },
            {
                "id": 24,
                "type": 1,
                "text": "Show me `Mamma Mia!` with your RIGHT hand",
                "link": os.path.join("emoji/omg.png")
            },
            {
                "id": 25,
                "type": 1,
                "text": "Show me `Mamma Mia!` with your LEFT hand",
                "link": os.path.join("emoji/omg.png")
            },

        ]

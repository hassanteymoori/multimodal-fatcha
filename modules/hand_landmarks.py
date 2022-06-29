import mediapipe as mp
import cv2
import config


class HandLandmark:
    def __init__(self, model_complexity=0, min_tracking_confidence=0.7, min_detection_confidence=0.7):
        self.model_complexity = model_complexity
        self.min_tracking_confidence = min_tracking_confidence
        self.min_detection_confidence = min_detection_confidence
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=self.model_complexity,
            min_tracking_confidence=self.min_tracking_confidence,
            min_detection_confidence=self.min_detection_confidence
        )

    def detect_with_landmarks(self, frame):
        return self.detect(frame, False, landmarks=True)

    def detect(self, frame, draw_bbox=False, landmarks=False):
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        hand_class_label = "Unknown"
        if results.multi_hand_landmarks:
            for hand_type, hand_landmarks in zip(results.multi_handedness, results.multi_hand_landmarks):
                hand_class_label = hand_type.classification[0].label
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())

                if draw_bbox:
                    self._draw_rectangle(frame, hand_landmarks.landmark, hand_type.classification[0].label)
        if landmarks:
            return frame, results, hand_class_label
        else:
            return frame, [], hand_class_label

    @staticmethod
    def _draw_rectangle(frame, landmarks, hand_type):
        height, width, _ = frame.shape
        landmarks_list = []
        x_list = []
        y_list = []

        for landmark in landmarks:
            px, py, pz = int(landmark.x * width), int(landmark.y * height), int(landmark.z * width)
            landmarks_list.append([px, py, pz])
            x_list.append(px)
            y_list.append(py)

        # bbox
        x_min, x_max = min(x_list), max(x_list)
        y_min, y_max = min(y_list), max(y_list)
        box_width, box_height = x_max - x_min, y_max - y_min
        bbox = x_min, y_min, box_width, box_height

        cv2.rectangle(
            frame,
            (bbox[0] - 20, bbox[1] - 20),
            (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
            config.hand["rectangle_color"],
            config.hand["rectangle_thickness"]
        )
        cv2.putText(
            frame,
            hand_type,
            (bbox[0] - 30, bbox[1] - 30),
            config.hand["font"],
            config.hand["font_scale"],
            config.hand["font_color"],
            config.hand["font_thickness"]
        )


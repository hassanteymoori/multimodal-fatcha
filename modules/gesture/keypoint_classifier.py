import numpy as np
import tensorflow as tf
import config
import cv2
import csv
from ..gesture.key_points_logging import CSVLogging


class KeyPointClassifier(object):
    def __init__(
            self,
            model_location=config.gesture["model_location"],
            num_threads=1,
    ):
        self.interpreter = tf.lite.Interpreter(model_path=model_location, num_threads=num_threads)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        with open(config.gesture["gestures_label"], encoding="utf-8-sig") as f:
            keypoint_classifier_labels = csv.reader(f)
            self.keypoint_classifier_labels = [
                row[0] for row in keypoint_classifier_labels
            ]

    @staticmethod
    def pre_processing(frame, landmarks):
        return CSVLogging.pre_process_landmark(
            CSVLogging.landmark_list(frame, landmarks)
        )

    def __call__(
            self,
            hand_face_detected_frame,
            landmark_list_original,
    ):
        landmark_list = self.pre_processing(hand_face_detected_frame, landmark_list_original)
        input_details_tensor_index = self.input_details[0]["index"]
        self.interpreter.set_tensor(
            input_details_tensor_index,
            np.array([landmark_list], dtype=np.float32))
        self.interpreter.invoke()

        output_details_tensor_index = self.output_details[0]["index"]

        result = self.interpreter.get_tensor(output_details_tensor_index)
        maximum = max(np.squeeze(result) * 100)
        if maximum <= 60:
            return 9, maximum
        result_index = np.argmax(np.squeeze(result))

        return result_index, maximum

    def show_on_screen(self, hand_face_detected_frame, results):
        gesture_class_id = -1
        if results.multi_hand_landmarks is not None:
            for h_landmarks in results.multi_hand_landmarks:
                gesture_class_id, maximum = self.__call__(hand_face_detected_frame, h_landmarks)
                cv2.putText(
                    hand_face_detected_frame,
                    "Finger Gesture: " + self.keypoint_classifier_labels[gesture_class_id] + "  : " + str(int(maximum)) + " %",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 0),
                    3,
                    cv2.LINE_AA
                )
        return hand_face_detected_frame, gesture_class_id

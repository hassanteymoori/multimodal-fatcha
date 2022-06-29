import config
import csv
import copy
import itertools


class CSVLogging:
    def __init__(self, location=config.gesture["logging"]):
        self.location = location
        self.flag = False

    def logging(self, frame, number_for_gesture, landmarks):

        processed_landmark = self.landmark_list(frame, landmarks)
        pre_processed_landmark_list = self.pre_process_landmark(processed_landmark)

        with open(self.location, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                number_for_gesture, *pre_processed_landmark_list
            ])

    @staticmethod
    def landmark_list(frame, landmarks):
        image_width, image_height = frame.shape[1], frame.shape[0]

        landmark_points = []
        for _, landmark in enumerate(landmarks.landmark):
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)

            landmark_points.append([landmark_x, landmark_y])

        return landmark_points

    @staticmethod
    def pre_process_landmark(landmark_list):
        temp_landmark_list = copy.deepcopy(landmark_list)

        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list

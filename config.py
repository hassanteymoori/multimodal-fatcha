import cv2
from logging import root
import os

root_dir = os.path.dirname(__file__)

# _________________________ camera config ______________________________ #

camera = {
    'width': 1920,
    'height': 1080
}

# _________________________ hand config ______________________________ #

hand = {
    'rectangle_color': (200, 0, 200),
    'rectangle_thickness': 2,

    'font': cv2.FONT_HERSHEY_PLAIN,
    'font_scale': 2,
    'font_color': (200, 0, 200),
    'font_thickness': 2
}

gesture = {
    'logging': os.path.join(root_dir, 'modules/gesture', 'key_points.csv'),
    'model_location': os.path.join(root_dir, 'modules/gesture/key_points_classifier.tflite'),
    'gestures_label': os.path.join(root_dir, 'modules/gesture/key_points_label.csv')
}

face = {
    'nose_tip' : 1,
    'corner_right_lip': 61,
    'corner_left_lip': 291,
    'corner_right_eye': 33,
    'corner_left_eye': 263,
    'chin': 199,
    'special_points_join': [1, 61, 291, 33,263, 199]
}
import os
import cv2
from keras.models import load_model
from keras.utils import img_to_array
import numpy as np

import config


class EmotionDetector:
    def __init__(self, model_location=os.path.join(os.path.dirname(__file__), 'cp-0017.h5')):
        self.model = load_model(model_location)
        self.labels = config.emotion

    def detect(self, frame, results):
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, c = frame.shape
                cx_min = w
                cy_min = h
                cx_max = cy_max = 0
                for id, lm in enumerate(face_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if cx < cx_min:
                        cx_min = cx
                    if cy < cy_min:
                        cy_min = cy
                    if cx > cx_max:
                        cx_max = cx
                    if cy > cy_max:
                        cy_max = cy

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                roi_gray = gray[cy_min:cy_max, cx_min:cx_max]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
                # bbox = np.array([cx_min, cy_min, (cx_max - cx_min), (cy_max - cy_min)])
                roi = roi_gray.astype('float') / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)
                # cv2.rectangle(frame, (cx_min, cy_min), (cx_max,  cy_max), (255, 0, 0), 2)
                predictions = self.model.predict(roi, verbose=0)[0]
                return predictions.argmax() , max(predictions) * 100
        else:
            return -1

    def label(self, class_id):
        return self.labels[class_id]

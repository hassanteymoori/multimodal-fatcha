import os
import cv2
import numpy as np
from keras.models import model_from_json
from keras.utils import img_to_array


class SpoofDetector:
    def __init__(self):
        root_dir = os.path.dirname(__file__)

        json_file = open(
            os.path.join(root_dir, 'model_net.json'),
            'r'
        )
        loaded_model_json = json_file.read()
        json_file.close()

        self.model = model_from_json(loaded_model_json)
        self.model.load_weights(
            os.path.join(root_dir, 'fake_or_real.h5')
        )
        self.face_detector = cv2.CascadeClassifier(
            os.path.join(root_dir, "haarcascade_frontalface_default.xml")
        )
        print("anti_spoofing model loaded.")
        self.n_consecutive_frames = 0
        self.detected = False
        self.text = ''
        self.result = False
        self.total = 0

    def next_consecutive(self, current_result):
        if current_result == 1:
            self.detected = True
            self.text = 'Possible spoof attack'
            self.n_consecutive_frames += 1
            self.total = 0
            if self.n_consecutive_frames >= 25:
                self.result = True
                self.n_consecutive_frames = 0
        elif current_result == 0:
            self.n_consecutive_frames = 0
            self.total += 1

        return

    def detect(self, frame):
        faces = self.face_detector.detectMultiScale(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
            1.3, 5
        )
        for (x, y, w, h) in faces:
            face = frame[y - 5:y + h + 5, x - 5:x + w + 5]
            roi_face = cv2.resize(face, (160, 160))
            roi_face = roi_face.astype("float") / 255.0
            roi_face = np.expand_dims(roi_face, axis=0)
            prediction = self.model.predict(roi_face, verbose=0)[0]
            if prediction > 0.2:
                class_id = 1
                label = 'spoof'

                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 0, 255), 2)
                return class_id, label
            else:
                class_id = 0
                label = 'real'
                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 255, 0), 2)
                return class_id, label
        return -1, 'No face, try to change pose in order to detect your face'

    def detect_mediapipe(self, frame, results):
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
                bbox = np.array([cx_min, cy_min, (cx_max - cx_min), (cy_max - cy_min)])
                if not sum(n < 0 for n in bbox) > 0:
                    # return self._detect(frame, bbox)
                    roi_face = frame[cy_min:cy_max, cx_min:cx_max]
                    roi_face = cv2.resize(roi_face, (160, 160), interpolation=cv2.INTER_AREA)
                    roi = roi_face.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)
                    # cv2.rectangle(frame, (cx_min, cy_min), (cx_max,  cy_max), (255, 0, 0), 2)
                    prediction = self.model.predict(roi, verbose=0)[0]
                    if prediction > 0.8:
                        class_id = 1
                        label = 'spoof'
                    else:
                        class_id = 0
                        label = 'real'
                    return class_id, label
                else:
                    return -1, 'No face'
        else:
            return -1, 'No face'

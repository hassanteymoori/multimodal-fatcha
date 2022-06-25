import cv2
import dlib
from imutils import face_utils


class FaceLandmarks:
    def __init__(self, model_location='model/shape_predictor_68_face_landmarks.dat'):
        # Load the detector
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(model_location)

    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rectangles = self.detector(gray, 0)

        # initialize dlib's face detector (HOG-based) and then create
        # the facial landmark predictor
        for rectangle in rectangles:
            (x, y, w, h) = face_utils.rect_to_bb(rectangle)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 1)

            landmarks = face_utils.shape_to_np(
                self.predictor(gray, rectangle)
            )

            for (x, y) in landmarks:
                # drawing points
                cv2.circle(image, (x, y), 2, (0, 255, 0), -1)
                cv2.putText(image, '.', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # jawline
        for rectangle in rectangles:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            landmarks = face_utils.shape_to_np(
                self.predictor(gray, rectangle)
            )

            for i in range(1, 17):
                (x1, y1) = landmarks[i - 1]
                (x2, y2) = landmarks[i]

                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 1)

        return image


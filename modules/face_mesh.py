import cv2
import mediapipe as mp


class FaceMesh:
    def __init__(self, min_tracking_confidence=0.7, min_detection_confidence=0.7):
        self.min_tracking_confidence = min_tracking_confidence
        self.min_detection_confidence = min_detection_confidence
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.drawing_spec = mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_tracking_confidence=self.min_tracking_confidence,
            min_detection_confidence=self.min_detection_confidence
        )

    def detect(self, frame):
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.drawing_spec,
                    connection_drawing_spec=self.drawing_spec)

        return frame

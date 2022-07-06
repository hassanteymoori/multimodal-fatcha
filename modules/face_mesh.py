import cv2
import mediapipe as mp
import numpy as np
import config


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

    def detect(self, frame, with_pose_estimator=False):
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if with_pose_estimator:
            return self.face_with_head_pose_estimator(frame, results)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self._draw_landmarks(frame, face_landmarks)

        return frame, 5, results  # default class which is forward

    def face_with_head_pose_estimator(self, frame, results):
        head_pose_class = -1  # default is forward
        frame_height, frame_width, _ = frame.shape
        face_3d = []
        face_2d = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for landmark_index, landmark in enumerate(face_landmarks.landmark):
                    if landmark_index in config.face["special_points_join"]:
                        x, y = int(landmark.x * frame_width), int(landmark.y * frame_height)

                        # Get the 2D Coordinates
                        face_2d.append([x, y])

                        # Get the 3D Coordinates
                        face_3d.append([x, y, landmark.z])

                # Convert it to the NumPy array
                face_2d = np.array(face_2d, dtype=np.float64)

                # Convert it to the NumPy array
                face_3d = np.array(face_3d, dtype=np.float64)

                # The camera matrix
                focal_length = 1 * frame_width

                cam_matrix = np.array([
                    [focal_length, 0, frame_height / 2],
                    [0, focal_length, frame_width / 2],
                    [0, 0, 1]
                ])

                # The distortion parameters
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                # Solve PnP
                success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                # Get rotational matrix
                rotational_matrix, jac = cv2.Rodrigues(rot_vec)

                # Get angles
                results_rq = cv2.RQDecomp3x3(rotational_matrix)
                angles = results_rq[0]

                # Get the y rotation degree
                x = angles[0] * 360
                y = angles[1] * 360

                # See where the user's head tilting
                if y < -10:
                    head_pose_class = 1  # Looking left
                elif y > 10:
                    head_pose_class = 2  # Looking right
                elif x < -10:
                    head_pose_class = 3  # Looking down
                elif x > 10:
                    head_pose_class = 4  # Looking up
                else:
                    head_pose_class = 5  # Looking forward

                self._draw_landmarks(frame, face_landmarks)

        return frame, head_pose_class, results

    def _draw_landmarks(self, frame, face_landmarks):
        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=self.drawing_spec,
            connection_drawing_spec=self.drawing_spec)

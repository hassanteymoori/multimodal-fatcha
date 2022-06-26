import cv2
import mediapipe as mp


class FaceDetection:

    def __init__(self, min_detection_confidence=0.6):
        self.min_detection_confidence = min_detection_confidence
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_draw = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(self.min_detection_confidence)

    def detect(self, frame):
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.detections:
            for detection in results.detections:
                self.mp_draw.draw_detection(frame, detection)

        return frame

        # bboxs = []
        # if self.results.detections:
        #     for id, detection in enumerate(self.results.detections):
        #         bboxC = detection.location_data.relative_bounding_box
        #         ih, iw, ic = img.shape
        #         bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
        #                int(bboxC.width * iw), int(bboxC.height * ih)
        #         cx, cy = bbox[0] + (bbox[2] // 2), \
        #                  bbox[1] + (bbox[3] // 2)
        #         bboxInfo = {"id": id, "bbox": bbox, "score": detection.score, "center": (cx, cy)}
        #         bboxs.append(bboxInfo)
        #         if draw:
        #             img = cv2.rectangle(img, bbox, (255, 0, 255), 2)
        #
        #             cv2.putText(img, f'{int(detection.score[0] * 100)}%',
        #                         (bbox[0], bbox[1] - 20), cv2.FONT_HERSHEY_PLAIN,
        #                         2, (255, 0, 255), 2)
        # return img, bboxs

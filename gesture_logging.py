import cv2
from modules.hand_landmarks import HandLandmark
from modules.gesture.key_points_logging import CSVLogging

cap = cv2.VideoCapture(0)

hand_landmarks = HandLandmark()
save_to_csv = CSVLogging()
gesture_class = -1

while cap.isOpened():
    # Read the frame
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame...")
        # If loading a video, use "break" instead of "continue".
        continue
    frame = cv2.flip(frame, 1)
    frame, results = hand_landmarks.detect_with_landmarks(frame)
    cv2.imshow("img", frame)

    key = cv2.waitKey(10)

    if 48 <= key <= 57:  # 0 ~ 9
        gesture_class = key - 48
        print("\n\033[92mYou pressed " + str(gesture_class) + " Logging the landmarks... to stop press `s` \033[0m")

    if key == 115:  # s --> start logging gestures or stop the logging
        gesture_class = -1
        print("\033[91mYou stopped Logging the landmarks, to start again, press another class\033[0m")

    if key == 27:  # ESC
        break

    if gesture_class != -1:
        if results is not None:
            for h_landmarks in results.multi_hand_landmarks:
                save_to_csv.logging(frame, gesture_class, h_landmarks)

cap.release()
import cv2
import config
import tkinter
from PIL import Image as PIL_Image
from PIL import ImageTk as PIL_ImageTk
from modules.hand_landmarks import HandLandmark
from modules.face_mesh import FaceMesh
from modules.gesture.keypoint_classifier import KeyPointClassifier
from modules.anti_spoofing.challenge.response import ChallengeResponse

face_mesh = FaceMesh()
hand_landmarks = HandLandmark()
key_points_classifier = KeyPointClassifier()
challenge = ChallengeResponse(config.challenge['number_of_challenges'])

cap = None  # To use a video file as input: cv2.VideoCapture("filename.mp4")
WARNING = '#db7d09'
INFO = '#a5ab35'
PRIMARY = '#3442bf'
BROWN = '#82636c'


def activate_webcam():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    label_general_info.configure(
        text="PRESS `s` to start the challenge",
        fg=INFO
    )
    btn_start.configure(state='disabled')
    visualize()


def visualize():
    success, frame = cap.read()
    if success:
        # frame = cv2.resize(frame, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC)
        returned_frame, head_pose_class = face_mesh.detect(
            cv2.flip(frame, 1),
            with_pose_estimator=True
        )
        head_pose_text = f'Pose: {config.head_pose[head_pose_class]}' if head_pose_class != -1 else 'Pose: Unknown'
        label_pose_info.configure(text=head_pose_text)

        returned_frame, results, hand_class_label = hand_landmarks.detect(
            returned_frame,
            draw_bbox=False,
            landmarks=True
        )
        returned_frame, gesture_class_id, predict_score = key_points_classifier.show_on_screen(
            returned_frame,
            results
        )
        gesture_text = key_points_classifier.keypoint_classifier_labels[gesture_class_id]
        if gesture_class_id != 9:
            gesture_text += f': {str(int(predict_score))} %'
        label_gesture_info.configure(text=f"Gesture: {gesture_text}")

        challenge.challenge_in_progress(
            returned_frame,
            {
                "head_pose_class": head_pose_class,
                "hand_class_label": hand_class_label,
                "gesture_class_id": gesture_class_id
            }
        )

        challenge.challenge_results(returned_frame)
        img = PIL_ImageTk.PhotoImage(
            image=PIL_Image.fromarray(
                cv2.cvtColor(returned_frame, cv2.COLOR_BGR2RGB)
            )
        )
        label_camera.configure(image=img, width=1280, height=720)
        label_camera.image = img
        label_camera.after(10, visualize)

    else:
        label_camera.image = ""
        cap.release()


window = tkinter.Tk()
window.geometry('1280x720')
window.title("Multimodal Fatcha")
window.columnconfigure(0, minsize=2)

btn_start = tkinter.Button(window, text="Start", relief=tkinter.RAISED, command=activate_webcam)
btn_start.grid(row=0, column=0, padx=5, pady=10)

frame_general_info = tkinter.Frame(window)
frame_general_info.grid(row=0, column=1, sticky="nsew", pady=10)
label_general_info = tkinter.Label(
    frame_general_info,
    text="",
    font=("Helvetica", 16),
    padx=2,
)
label_general_info.grid(row=0, column=0, sticky="nsew", pady=10)
label_channel_info = tkinter.Label(
    frame_general_info,
    text="",
    font=("Helvetica", 16),
    padx=2,
)
label_channel_info.grid(row=0, column=1, sticky="nsew", pady=10)

frame_detail_info = tkinter.Frame(window)
frame_detail_info.grid(row=0, column=2, sticky="nsew", pady=10, padx=1)

label_pose_info = tkinter.Label(
    frame_detail_info,
    text="",
    anchor="w",
    font=("Helvetica", 16),
    fg=PRIMARY,
)
label_pose_info.grid(column=0, row=0, sticky='w', pady=0)
label_gesture_info = tkinter.Label(
    frame_detail_info,
    text="",
    anchor="w",
    font=("Helvetica", 16),
    fg=BROWN,
)
label_gesture_info.grid(column=0, row=1, sticky='w', pady=0)

label_camera = tkinter.Label(window)
label_camera.grid(row=1, column=0, columnspan=3, sticky="nsew")


# Define an event to close the window
def close_win(e):
    window.destroy()


def start_ch(e):
    if cap is not None and cap.isOpened():
        challenge.start_challenge()
    else:
        label_general_info.configure(
            text="Warning: You need to start the FATCHA first!",
            fg=WARNING
        )


# Bind the ESC and q keys with the callback function
window.bind('<Escape>', lambda event: close_win(event))
window.bind('q', lambda event: close_win(event))
window.bind('s', lambda event: start_ch(event))

window.mainloop()



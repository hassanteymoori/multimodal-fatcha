import cv2
import config
import tkinter
from PIL import Image as PIL_Image
from PIL import ImageTk as PIL_ImageTk
from modules.hand_landmarks import HandLandmark
from modules.face_mesh import FaceMesh
from modules.gesture.keypoint_classifier import KeyPointClassifier
from modules.anti_spoofing.challenge.response import ChallengeResponse
from modules.anti_spoofing.emotion.emotion_detection import EmotionDetector
from modules.anti_spoofing.fake_or_spoof.spoof_detection import SpoofDetector
from modules.voice_assistant import VoiceAssistant
from tkinter import ttk
import os

face_mesh = FaceMesh()
hand_landmarks = HandLandmark()
key_points_classifier = KeyPointClassifier()
emotion_detector = EmotionDetector()
voice_assistant = VoiceAssistant()
challenge = ChallengeResponse(voice_assistant, config.challenge['number_of_challenges'])
spoof_detector = SpoofDetector()

cap = None  # To use a video file as input: cv2.VideoCapture("filename.mp4")
WARNING = '#db7d09'
INFO = '#a5ab35'
PRIMARY = '#3442bf'
BROWN = '#82636c'
GREEN = '#2fcc4e'
DANGER = '#cc1c08'
YELLOW = '#baa53d'
LIGHTBLUE = '#48b1cf'

voice_assistant.welcome()


def about_window():
    top2 = tkinter.Toplevel(window)
    top2.title("About")
    top2.resizable(False, False)

    explanation = "This is a project  related to the \n Multimodal interaction course"

    ttk.Label(top2, justify=tkinter.LEFT, text=explanation).pack(padx=5, pady=2)
    ttk.Button(top2, text='OK', width=10, command=top2.destroy).pack(pady=8)

    top2.transient(window)
    top2.grab_set()
    window.wait_window(top2)


def init_webcam():
    global cap
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


def confirm_real():
    txt = 'Try to be neutral in front of the camera, the procedure will take some seconds to be done;'
    txt += ' We are kindly asking you to be patient during the procedure!'

    voice_assistant.kill_previous_and_speak(txt)
    init_webcam()
    spoof_process()


def activate_webcam():
    init_webcam()
    txt = 'PRESS `s` to start the challenge'
    voice_assistant.kill_previous_and_speak(txt)

    label_general_info.configure(
        text=txt,
        fg=INFO
    )
    btn_start.configure(state='disabled')
    visualize()


def spoof_process():
    success, frame = cap.read()

    if success:
        spoof_id, spoof_label = spoof_detector.detect(frame)
        spoof_detector.next_consecutive(spoof_id)
        if spoof_detector.total >= 100:
            label_camera.image = ""
            cap.release()
            label_general_info.configure(text="Real identity: You can  use the system", fg='Green')
            btn_spoof.destroy()
            btn_start.configure(state='normal')
            label_spoof_info.destroy()
            txt = 'You have been recognized as a real identity, so we let you to use the system! '
            txt += 'Press `start the Fatcha` please!'
            voice_assistant.kill_previous_and_speak(txt)

        else:
            if spoof_detector.n_consecutive_frames >= 1:
                label_emotion_info.configure(text="Alert: possible spoofing!", fg='red')
            else:
                label_emotion_info.configure(text="")

            if spoof_detector.result:
                label_camera.image = ""
                cap.release()
                label_emotion_info.configure(text="SPOOFING: You can not use the system", fg='red')
                voice_assistant.kill_previous_and_speak(
                    'You have been recognized as a real identity, so we let you to use the system! '
                )
                voice_assistant.kill_previous_and_speak(
                    'We are really sorry to say that it seems you are trying to foul the system!'
                )
                btn_spoof.configure(state='disabled')

            spoof_text = "Face: "
            if spoof_id != -1:
                spoof_text += spoof_label
                label_spoof_info.configure(text=spoof_text, fg=PRIMARY)
            else:
                spoof_text += spoof_label
                label_spoof_info.configure(text=spoof_text, fg=INFO)

        img = PIL_ImageTk.PhotoImage(
            image=PIL_Image.fromarray(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )
        )
        label_camera.configure(image=img, width=1280, height=720)
        label_camera.image = img
        label_camera.after(10, spoof_process)

    else:
        label_camera.image = ""
        cap.release()


def visualize():
    success, frame = cap.read()
    if success:
        # frame = cv2.resize(frame, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC)
        returned_frame, head_pose_class, results = face_mesh.detect(
            cv2.flip(frame, 1),
            with_pose_estimator=True
        )
        emotion_class_id, max_emotion = emotion_detector.detect(frame, results)
        emotion_text = "Emotion: "
        if emotion_class_id != -1:
            emotion_text += emotion_detector.label(emotion_class_id)
            emotion_text += f' {str(int(max_emotion))} %'
        else:
            emotion_text += ' Unknown'
        label_emotion_info.configure(text=emotion_text)

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
                "gesture_class_id": gesture_class_id,
                'emotion_class_id': emotion_class_id
            },
        )

        if challenge.is_challenge_in_progress():
            label_channel_info.configure(
                text=challenge.text,
                fg=GREEN if challenge.detected else PRIMARY,
                font=('Helvetica', 20),
            )
            if challenge.questions[challenge.current_question]['type'] == 1:
                icon = PIL_ImageTk.PhotoImage(
                    image=PIL_Image.fromarray(
                        cv2.cvtColor(
                            cv2.resize(
                                cv2.imread(challenge.questions[challenge.current_question]['link']),
                                (70, 70)
                            ),
                            cv2.COLOR_BGR2RGB
                        )
                    )
                )
                label_icon.configure(image=icon)
                label_icon.image = icon
            if challenge.is_on_going():
                label_general_info.configure(
                    text=challenge.total_attempt_text,
                    fg=DANGER,
                )
        if challenge.is_access_granted():
            if voice_assistant.active and not voice_assistant.granted_notified:
                voice_assistant.granted_notified = True
                voice_assistant.kill_previous_and_speak(
                    'congratulations, you have been granted to access the system!'
                )
            label_general_info.configure(
                text='Access Granted Successfully',
                fg=GREEN,
                font=('Helvetica', 20),
            )
            label_icon.image = ''
            label_icon.configure(image='')
            label_channel_info.configure(text='')
        if challenge.is_access_denied():
            if voice_assistant.active and not voice_assistant.granted_notified:
                voice_assistant.granted_notified = True
                voice_assistant.kill_previous_and_speak(
                    'Unfortunately, you have not been able to pass our challenges, Access Denied!'
                )
            label_general_info.configure(
                text='Access Denied ... !',
                fg=DANGER,
                font=('Helvetica', 20),
            )
            label_icon.image = ''
            label_icon.configure(image='')
            label_channel_info.configure(text='')

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


# Define an event to close the window
def close_win(e):
    window.destroy()


def start_ch(e):
    if cap is not None and cap.isOpened():
        challenge.start_challenge()
    else:
        txt = 'Warning: You need to start the FATCHA first!'
        voice_assistant.stop_current_thread()
        voice_assistant.synthesize_thread(txt)
        label_general_info.configure(
            text=txt,
            fg=WARNING
        )


def voice_channel(e=''):
    voice_assistant.stop_current_thread()
    if voice_assistant.active:
        voice_assistant.change_state()
        btn_voice.configure(text='voice disabled!', fg=BROWN)
        voice_assistant.synthesize_thread(
            'Voice output channel deactivated! You can activate it anytime by pressing v again'
        )
    else:
        voice_assistant.change_state()
        btn_voice.configure(text='Voice activated!', fg=GREEN)
        voice_assistant.synthesize_thread(
            'Voice output channel activated! You can de-activate it anytime by pressing v again'
        )


def listening(e=''):
    voice_assistant.stop_current_thread()
    result = voice_assistant.listen_and_process()
    print(result)
    if result != 0:
        match result:
            case 1:
                return window.destroy()
            case 2:
                return confirm_real()
            case 3:
                return start_ch('')
            case 4:
                voice_assistant.stop_current_thread()
                voice_assistant.synthesize_thread(
                    'The given command has not been defined in this system!'
                )
            case _:
                return


def help_win():
    top = tkinter.Toplevel(window)
    top.title("About")
    top.resizable(False, False)

    top.columnconfigure(0, weight=1)
    top.columnconfigure(1, weight=3)

    # exit
    ttk.Label(top, text="<Escape> or q").grid(column=0, row=0, sticky=tkinter.W, padx=5, pady=5)
    ttk.Label(top, text="Exit from the app").grid(column=1, row=0, sticky=tkinter.E, padx=5, pady=5)

    # voice output channel
    ttk.Label(top, text="v").grid(column=0, row=1, sticky=tkinter.W, padx=5, pady=5)
    ttk.Label(top, text="to activate/deactivate voice OUTPUT channel").grid(
        column=1,
        row=1,
        sticky=tkinter.E,
        padx=5,
        pady=5
    )
    # voice input channel
    ttk.Label(top, text="l").grid(column=0, row=2, sticky=tkinter.W, padx=5, pady=5)
    ttk.Label(top, text="to activate/deactivate voice INPUT channel").grid(
        column=1,
        row=2,
        sticky=tkinter.E,
        padx=5,
        pady=5
    )
    ttk.Label(top, text="s").grid(column=0, row=3, sticky=tkinter.W, padx=5, pady=5)
    ttk.Label(top, text="to start the challenge").grid(
        column=1,
        row=3,
        sticky=tkinter.E,
        padx=5,
        pady=5
    )

    ttk.Button(top, text='OK', width=10, command=top.destroy).pack(pady=8)
    top.transient(window)
    top.grab_set()
    window.wait_window(top)


window = tkinter.Tk()
window.resizable(False, False)
window.style = ttk.Style()
window.style.theme_use("clam")  # ('clam', 'alt', 'default', 'classic')
window.geometry('1280x815')
window.title("Multimodal Fatcha")
window.columnconfigure(0, minsize=2)

menu = tkinter.Menu(window)
window.config(menu=menu)
fm = tkinter.Menu(menu, tearoff=0)
menu.add_cascade(label="Settings", menu=fm)
fm.add_command(label="Preferences")
fm.add_command(label="Activate Voice", command=voice_channel)

hm = tkinter.Menu(menu, tearoff=0)
menu.add_cascade(label="Help", menu=hm)
hm.add_command(label="About", command=about_window)
hm.add_command(label="Help", command=help_win)
hm.add_command(label="Exit", command=window.quit)

btn_panel = tkinter.Frame(window)
btn_panel.grid(row=0, column=0, sticky="nsew")

btn_voice = tkinter.Button(
    btn_panel,
    text="Voice is active!",
    relief=tkinter.RAISED,
    command=voice_channel,
    fg=GREEN
)
btn_voice.grid(row=0, column=0)

btn_spoof = tkinter.Button(
    btn_panel,
    text="Spoof or Real!",
    relief=tkinter.RAISED,
    command=confirm_real,
)
btn_spoof.grid(row=1, column=0, padx=5)

btn_start = tkinter.Button(
    btn_panel,
    text="Start the Fatcha",
    relief=tkinter.RAISED,
    command=activate_webcam,
    state='disabled'
)
btn_start.grid(row=2, column=0, padx=5)

right_panel = tkinter.Frame(window)
right_panel.grid(row=0, column=1, sticky="nsew", pady=10)

label_pose_info = tkinter.Label(
    right_panel,
    text="",
    anchor="w",
    font=("Helvetica", 16),
    fg=PRIMARY,
)
label_pose_info.grid(column=0, row=0, sticky='w', pady=0)
label_gesture_info = tkinter.Label(
    right_panel,
    text="",
    anchor="w",
    font=("Helvetica", 16),
    fg=BROWN,
)
label_gesture_info.grid(column=0, row=1, sticky='w', pady=0)
label_emotion_info = tkinter.Label(
    right_panel,
    text="",
    anchor="w",
    font=("Helvetica", 16),
    fg=LIGHTBLUE,
)
label_emotion_info.grid(column=0, row=2, sticky='w', pady=0)

center_panel = tkinter.Frame(window)
center_panel.grid(row=0, column=2, sticky="nsew", pady=10)
label_general_info = tkinter.Label(
    center_panel,
    text="",
    font=("Helvetica", 16),
    padx=2,
)
label_general_info.grid(row=0, column=0, sticky="nsew")
label_channel_info = tkinter.Label(
    center_panel,
    text="",
    font=("Helvetica", 16),
    padx=2,
)
label_channel_info.grid(row=1, column=0, sticky="nsew")

label_spoof_info = tkinter.Label(
    center_panel,
    text="",
    font=("Helvetica", 16),
    padx=2,
    fg="Green"
)
label_spoof_info.grid(row=3, column=0, sticky="nsew")

label_icon = tkinter.Label(window, anchor='e')
label_icon.grid(row=0, column=3, sticky="nsew")

label_camera = tkinter.Label(window)
label_camera.grid(row=1, column=0, columnspan=4, sticky="nsew")

cv2_img = cv2.resize(
    cv2.imread(os.path.join(os.path.dirname(__file__), 'background.jpeg')), (720, 480)
)
img = PIL_ImageTk.PhotoImage(
    image=PIL_Image.fromarray(
        cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    )
)
label_camera.configure(image=img, width=1280, height=720)
label_camera.image = img

# Bind the ESC and q keys with the callback function
window.bind('<Escape>', lambda event: close_win(event))
window.bind('q', lambda event: close_win(event))
window.bind('s', lambda event: start_ch(event))
window.bind('v', lambda event: voice_channel(event))
window.bind('l', lambda event: listening(event))
window.mainloop()

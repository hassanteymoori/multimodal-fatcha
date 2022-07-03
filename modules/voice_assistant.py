import datetime
import azure.cognitiveservices.speech as speechsdk
import config
import threading
import random
import re


class VoiceAssistant:
    def __init__(self):
        speech_config = speechsdk.SpeechConfig(
            subscription=config.azure['key'],
            region=config.azure['region']
        )
        # Output
        audio_config = speechsdk.audio.AudioOutputConfig(
            use_default_speaker=True
        )

        speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'

        self.active = True
        self.notified = False
        self.granted_notified = False
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        self.current_thread = None

        # input
        speech_config.speech_recognition_language = "en-US"
        audio_input_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_input_config
        )

    def synthesize(self, text):
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")

    def synthesize_thread(self, text):
        self.current_thread = threading.Thread(target=self.synthesize, args=(text,), daemon=True)
        self.current_thread.start()

    def stop_current_thread(self):
        self.speech_synthesizer.stop_speaking_async()

    def change_state(self):
        self.active = not self.active

    def kill_previous_and_speak(self, text):
        if self.active:
            self.stop_current_thread()
            self.synthesize_thread(
                text
            )

    def welcome(self):
        hour = int(datetime.datetime.now().hour)
        welcome_txt = ''
        if 0 <= hour < 12:
            welcome_txt += "good morning; "
        elif 12 <= hour < 18:
            welcome_txt += "good afternoon; "
        else:
            welcome_txt += "good evening; "

        welcome_txt += ' welcome to the multimodal Fatcha application. '
        welcome_txt += ' If you want to disable the voice output channel press v. '
        welcome_txt += ' To re-activate it,  press v again.'
        welcome_txt += ' The first thing you need to do is to start the spoofing detection procedure;.'
        welcome_txt += ' The spoofing detection procedure will be started by Press the ` Spoof or Real!`'
        welcome_txt += " Be aware that, you won't be able to do anything unless to pass the procedure"
        self.synthesize_thread(welcome_txt)

    def _listening(self):
        print("Listening...")
        speech_recognition_result = self.speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

        return speech_recognition_result.text

    def listen_and_process(self):
        result = self._listening()

        if re.search(result, 'Hello, Hi, Hey', re.IGNORECASE):
            self.stop_current_thread()
            self.synthesize_thread(
                random.choice(
                    ['Hi there', 'Hello', 'Hi', 'Hey', 'Hey there']
                )
            )
            return 0
        if re.search(result, 'Exit, quit, close, finish,  Exit, please.', re.IGNORECASE):
            self.stop_current_thread()
            self.synthesize_thread('Are you sure that you want to exit?')
            confirm = self._listening()
            if re.search(confirm, 'Yes, sure, absolutely, of course, yeah, yes please!', re.IGNORECASE):
                return 1
            else:
                return 0
        if re.search(result, 'Activate voice output channel. , Activate the voice output channel. ', re.IGNORECASE):
            if self.active:
                self.stop_current_thread()
                self.synthesize(
                    'Voice output channel is already active! Would you like me to deactivate it?'
                )
                confirm = self._listening()
                if re.search(confirm, 'Yes, sure, absolutely, of course, yeah, yes please!', re.IGNORECASE):
                    self.stop_current_thread()
                    self.active = False
                    self.synthesize_thread('voice output channel deactivated!')
            else:
                self.stop_current_thread()
                self.active = True
                self.synthesize_thread('voice output channel activated!')
            return 0
        if re.search(result, 'deactivate voice output channel. deactivate the voice output channel. !', re.IGNORECASE):
            if not self.active:
                self.stop_current_thread()
                self.synthesize(
                    'Voice output channel has been already deactivated! Would you like me to activate it?'
                )
                confirm = self._listening()
                if re.search(confirm, 'Yes, sure, absolutely, of course, yeah, yes please! yes thank you',
                             re.IGNORECASE):
                    self.stop_current_thread()
                    self.active = True
                    self.synthesize_thread('voice output channel activated!')
                return 0
            else:
                self.stop_current_thread()
                self.active = False
                self.synthesize_thread('voice output channel deactivated!')
            return 0

import datetime
import azure.cognitiveservices.speech as speechsdk
import config
import threading


class VoiceAssistant:
    def __init__(self):
        speech_config = speechsdk.SpeechConfig(
            subscription=config.azure['key'],
            region=config.azure['region']
        )
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
        welcome_txt += ' If you want to disable the voice channel press v. '
        welcome_txt += ' To re-activate it,  press v again.'
        welcome_txt += ' The first thing you need to do is to start the spoofing detection procedure;.'
        welcome_txt += ' The spoofing detection procedure will be started by Press the ` Spoof or Real!`'
        welcome_txt += " Be aware that, you won't be able to do anything unless to pass the procedure"
        self.synthesize_thread(welcome_txt)

    # def command(self, ):
    #


    def response(self):

        if 'ready' in self.query:
            self.speak(
                'You have chosen the voice communication. At the first step we kindly want you to show the demanded sticker with your hand in front of the camera ')

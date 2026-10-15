import pyttsx3
import threading


class AIVoice:

    def __init__(self):

        self.engine = pyttsx3.init()

        self.engine.setProperty("rate", 170)
        self.engine.setProperty("volume", 1.0)

        voices = self.engine.getProperty("voices")

        if len(voices) > 1:
            self.engine.setProperty("voice", voices[1].id)

    def speak(self, text: str):

        threading.Thread(
            target=self._speak_thread,
            args=(text,),
            daemon=True
        ).start()

    def _speak_thread(self, text: str):

        self.engine.say(text)
        self.engine.runAndWait()
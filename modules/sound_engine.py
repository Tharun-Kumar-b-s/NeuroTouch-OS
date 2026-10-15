from playsound import playsound
import threading


class SoundEngine:

    def play(self, sound_path: str):

        threading.Thread(
            target=self._play_thread,
            args=(sound_path,),
            daemon=True
        ).start()

    @staticmethod
    def _play_thread(sound_path: str):

        try:
            playsound(sound_path)

        except:
            pass
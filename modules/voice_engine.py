# """
# NeuroTouch OS — Voice Recognition Module
# ==========================================
# Threaded speech recognition using SpeechRecognition library.
# Runs in a dedicated daemon thread to never block the main loop.
# Commands are pushed to a thread-safe queue for the main loop to consume.
# """

# import speech_recognition as sr
# import threading
# import queue
# import time
# from typing import Optional
# import config as cfg


# # Supported voice commands mapped to action identifiers
# VOICE_COMMANDS = {
#     "click": "left_click",
#     "left click": "left_click",
#     "double click": "double_click",
#     "right click": "right_click",
#     "scroll up": "scroll_up",
#     "scroll down": "scroll_down",
#     "stop scroll": "stop_scroll",
#     "stop scrolling": "stop_scroll",
#     "stop": "stop_scroll",
#     "keyboard": "keyboard_open",
#     "open keyboard": "keyboard_open",
#     "close keyboard": "keyboard_close",
#     "hide keyboard": "keyboard_close",
# }


# class VoiceEngine:
#     """
#     Threaded voice recognition engine.
    
#     Runs speech recognition in a background daemon thread. Recognized
#     commands are placed in a thread-safe queue that the main loop polls
#     each frame (non-blocking).
    
#     Uses Google Speech API for recognition (requires internet).
#     """

#     def __init__(self):
#         self._recognizer = sr.Recognizer()
#         self._recognizer.energy_threshold = cfg.VOICE_ENERGY_THRESHOLD
#         self._recognizer.pause_threshold = cfg.VOICE_PAUSE_THRESHOLD
#         self._recognizer.dynamic_energy_threshold = True

#         self._command_queue: queue.Queue = queue.Queue(maxsize=5)
#         self._thread: Optional[threading.Thread] = None
#         self._running = False
#         self._last_raw_text = ""
#         self._status = "Initializing..."
#         self._lock = threading.Lock()

#     @property
#     def status(self) -> str:
#         """Current voice engine status (thread-safe)."""
#         with self._lock:
#             return self._status

#     @property
#     def last_text(self) -> str:
#         """Last recognized raw text (thread-safe)."""
#         with self._lock:
#             return self._last_raw_text

#     def start(self) -> None:
#         """Start the voice recognition thread."""
#         if self._running:
#             return
#         self._running = True
#         self._thread = threading.Thread(target=self._listen_loop, daemon=True)
#         self._thread.start()
#         with self._lock:
#             self._status = "Listening..."

#     def stop(self) -> None:
#         """Stop the voice recognition thread."""
#         self._running = False
#         if self._thread:
#             self._thread.join(timeout=3)
#         with self._lock:
#             self._status = "Stopped"

#     def poll_command(self) -> Optional[str]:
#         """
#         Non-blocking poll for the next voice command.
        
#         Called by the main loop each frame. Returns the action identifier
#         string if a command is available, None otherwise.
        
#         Returns:
#             Action string (e.g., "left_click") or None
#         """
#         try:
#             return self._command_queue.get_nowait()
#         except queue.Empty:
#             return None

#     def _listen_loop(self) -> None:
#         """
#         Main listening loop (runs in background thread).
        
#         Continuously listens for speech, recognizes it, matches against
#         known commands, and pushes to the queue.
#         """
#         try:
#             mic = sr.Microphone()
#         except (OSError, AttributeError) as e:
#             with self._lock:
#                 self._status = f"Mic Error: {e}"
#             return

#         with mic as source:
#             # Calibrate for ambient noise on startup
#             with self._lock:
#                 self._status = "Calibrating mic..."
#             self._recognizer.adjust_for_ambient_noise(source, duration=1.0)
#             with self._lock:
#                 self._status = "Listening..."

#         while self._running:
#             try:
#                 with mic as source:
#                     # Listen with timeout to allow thread exit checks
#                     audio = self._recognizer.listen(
#                         source,
#                         timeout=cfg.VOICE_LISTEN_TIMEOUT,
#                         phrase_time_limit=cfg.VOICE_PHRASE_TIME_LIMIT,
#                     )

#                 # Recognize speech using Google API
#                 with self._lock:
#                     self._status = "Processing..."

#                 text = self._recognizer.recognize_google(audio).lower().strip()

#                 with self._lock:
#                     self._last_raw_text = text
#                     self._status = f'Heard: "{text}"'

#                 # Match against known commands
#                 action = self._match_command(text)
#                 if action:
#                     # Push to queue (non-blocking, discard if full)
#                     try:
#                         self._command_queue.put_nowait(action)
#                     except queue.Full:
#                         pass

#             except sr.WaitTimeoutError:
#                 # No speech detected within timeout — normal, continue
#                 with self._lock:
#                     self._status = "Listening..."
#             except sr.UnknownValueError:
#                 # Speech was unintelligible — ignore
#                 with self._lock:
#                     self._status = "Listening..."
#             except sr.RequestError as e:
#                 # API error
#                 with self._lock:
#                     self._status = f"API Error"
#                 time.sleep(1)  # Brief pause before retry
#             except Exception as e:
#                 with self._lock:
#                     self._status = f"Error: {type(e).__name__}"
#                 time.sleep(0.5)

#     @staticmethod
#     def _match_command(text: str) -> Optional[str]:
#         """
#         Match recognized text against known voice commands.
        
#         Uses substring matching for robustness against slight
#         misrecognitions. Longer commands are checked first to
#         prevent "click" from matching before "double click".
        
#         Args:
#             text: Recognized text (lowercase, stripped)
            
#         Returns:
#             Action identifier string or None
#         """
#         # Sort commands by length (descending) to match longest first
#         # This prevents "click" matching before "double click"
#         sorted_commands = sorted(VOICE_COMMANDS.keys(), key=len, reverse=True)

#         for phrase in sorted_commands:
#             if phrase in text:
#                 return VOICE_COMMANDS[phrase]

#         return None


"""
NeuroTouch OS — Voice Recognition Module
==========================================
Threaded speech recognition using SpeechRecognition library.
Runs in a dedicated daemon thread to never block the main loop.
"""

import speech_recognition as sr
import threading
import queue
import time
from typing import Optional
import config as cfg


# ============================================================
# VOICE COMMANDS
# ============================================================

VOICE_COMMANDS = {

    # Mouse
    "click": "left_click",
    "left click": "left_click",
    "right click": "right_click",
    "double click": "double_click",

    # Scroll
    "scroll up": "scroll_up",
    "scroll down": "scroll_down",
    "stop scroll": "stop_scroll",
    "stop scrolling": "stop_scroll",
    "stop": "stop_scroll",

    # Keyboard
    "keyboard": "keyboard_open",
    "open keyboard": "keyboard_open",
    "close keyboard": "keyboard_close",
    "hide keyboard": "keyboard_close",

    # Window Controls
    "minimize": "minimize_window",
    "maximize": "maximize_window",
    "close": "close_window",

    # Apps
    "open chrome": "open_chrome",
    "open whatsapp": "open_whatsapp",
    "open explorer": "open_explorer",
}


class VoiceEngine:

    def __init__(self):

        self._recognizer = sr.Recognizer()

        self._recognizer.energy_threshold = (
            cfg.VOICE_ENERGY_THRESHOLD
        )

        self._recognizer.pause_threshold = (
            cfg.VOICE_PAUSE_THRESHOLD
        )

        self._recognizer.dynamic_energy_threshold = True

        # IMPORTANT FIX
        self._recognizer.non_speaking_duration = 0.3

        self._command_queue: queue.Queue = (
            queue.Queue(maxsize=5)
        )

        self._thread: Optional[
            threading.Thread
        ] = None

        self._running = False

        self._last_raw_text = ""

        self._status = "Initializing..."

        self._lock = threading.Lock()

    # ============================================================
    # STATUS
    # ============================================================

    @property
    def status(self) -> str:

        with self._lock:
            return self._status

    @property
    def last_text(self) -> str:

        with self._lock:
            return self._last_raw_text

    # ============================================================
    # START
    # ============================================================

    def start(self) -> None:

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )

        self._thread.start()

        with self._lock:
            self._status = "Listening..."

    # ============================================================
    # STOP
    # ============================================================

    def stop(self) -> None:

        self._running = False

        if self._thread:

            self._thread.join(timeout=3)

        with self._lock:
            self._status = "Stopped"

    # ============================================================
    # POLL COMMAND
    # ============================================================

    def poll_command(self) -> Optional[str]:

        try:
            return self._command_queue.get_nowait()

        except queue.Empty:
            return None

    # ============================================================
    # LISTEN LOOP
    # ============================================================

    def _listen_loop(self) -> None:

        try:

            mic = sr.Microphone()

        except (OSError, AttributeError) as e:

            with self._lock:
                self._status = f"Mic Error: {e}"

            return

        # ========================================================
        # MIC CALIBRATION
        # ========================================================

        with mic as source:

            with self._lock:
                self._status = "Calibrating mic..."

            try:

                self._recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1.0
                )

            except Exception:

                pass

            with self._lock:
                self._status = "Listening..."

        # ========================================================
        # MAIN LOOP
        # ========================================================

        while self._running:

            try:

                with mic as source:

                    audio = self._recognizer.listen(
                        source,
                        timeout=cfg.VOICE_LISTEN_TIMEOUT,
                        phrase_time_limit=cfg.VOICE_PHRASE_TIME_LIMIT,
                    )

                with self._lock:
                    self._status = "Processing..."

                text = self._recognizer.recognize_google(
                    audio
                ).lower().strip()

                with self._lock:

                    self._last_raw_text = text

                    self._status = (
                        f'Heard: "{text}"'
                    )

                action = self._match_command(text)

                if action:

                    try:

                        self._command_queue.put_nowait(
                            action
                        )

                    except queue.Full:

                        pass

            except sr.WaitTimeoutError:

                with self._lock:
                    self._status = "Listening..."

            except sr.UnknownValueError:

                with self._lock:
                    self._status = "Listening..."

            except sr.RequestError:

                with self._lock:
                    self._status = "API Error"

                time.sleep(1)

            except Exception as e:

                with self._lock:

                    self._status = (
                        f"Error: {type(e).__name__}"
                    )

                time.sleep(0.5)

    # ============================================================
    # COMMAND MATCHING
    # ============================================================

    @staticmethod
    def _match_command(
        text: str
    ) -> Optional[str]:

        sorted_commands = sorted(
            VOICE_COMMANDS.keys(),
            key=len,
            reverse=True
        )

        for phrase in sorted_commands:

            if phrase in text:

                return VOICE_COMMANDS[phrase]

        return None
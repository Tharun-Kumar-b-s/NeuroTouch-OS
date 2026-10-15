"""
NeuroTouch OS — Drowsiness Detection System
=============================================
Monitors Eye Aspect Ratio (EAR) for prolonged eye closure.
Triggers audible alarm and visual warning after configurable threshold.
"""

import time
import threading
import winsound
from typing import Optional
import config as cfg


class DrowsinessDetector:
    """
    Detects prolonged eye closure and triggers alarm.
    
    If EAR stays below threshold for DROWSINESS_ALARM_DELAY seconds,
    alarm sounds until eyes reopen.
    """

    def __init__(self):
        self._eyes_closed_since: Optional[float] = None
        self._alarm_active = False
        self._alarm_thread: Optional[threading.Thread] = None
        self._stop_alarm_event = threading.Event()

    @property
    def alarm_active(self) -> bool:
        return self._alarm_active

    @property
    def eyes_closed_duration(self) -> float:
        if self._eyes_closed_since is None:
            return 0.0
        return time.time() - self._eyes_closed_since

    def update(self, ear: Optional[float]) -> bool:
        """Update with new EAR reading. Returns True if alarm is active."""
        if ear is None:
            self._reset_timer()
            return False

        if ear < cfg.EAR_THRESHOLD:
            if self._eyes_closed_since is None:
                self._eyes_closed_since = time.time()
            elapsed = time.time() - self._eyes_closed_since
            if elapsed >= cfg.DROWSINESS_ALARM_DELAY and not self._alarm_active:
                self._start_alarm()
            return self._alarm_active
        else:
            if self._alarm_active:
                self._stop_alarm()
            self._reset_timer()
            return False

    def _reset_timer(self):
        self._eyes_closed_since = None

    def _start_alarm(self):
        self._alarm_active = True
        self._stop_alarm_event.clear()
        self._alarm_thread = threading.Thread(target=self._alarm_loop, daemon=True)
        self._alarm_thread.start()

    def _stop_alarm(self):
        self._alarm_active = False
        self._stop_alarm_event.set()
        if self._alarm_thread:
            self._alarm_thread.join(timeout=1)

    def _alarm_loop(self):
        while not self._stop_alarm_event.is_set():
            try:
                winsound.Beep(cfg.DROWSINESS_BEEP_FREQ, cfg.DROWSINESS_BEEP_DURATION)
            except Exception:
                pass
            self._stop_alarm_event.wait(0.2)

    def release(self):
        if self._alarm_active:
            self._stop_alarm()

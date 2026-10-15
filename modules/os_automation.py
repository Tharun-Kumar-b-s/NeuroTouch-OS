# """
# NeuroTouch OS — OS Automation Layer
# =====================================
# Handles all operating system interactions:
# - Mouse clicks (left, right, double)
# - Scrolling (continuous, voice-controlled)
# - Safety settings
# """

# import pyautogui
# import time
# from typing import Optional
# import config as cfg


# # PyAutoGUI safety settings
# pyautogui.FAILSAFE = False         # Move mouse to top-left corner to abort
# pyautogui.PAUSE = 0               # No pause between actions (we handle our own cooldowns)


# class OSAutomation:
#     """
#     Handles all OS-level automation actions.
    
#     Uses PyAutoGUI for clicks and scrolling.
#     Maintains scroll state for continuous voice-controlled scrolling.
#     """

#     def __init__(self):
#         self._scroll_active = False
#         self._scroll_direction: int = 0       # +1 = up, -1 = down
#         self._last_scroll_time: float = 0.0

#     @property
#     def is_scrolling(self) -> bool:
#         """Whether continuous scrolling is active."""
#         return self._scroll_active

#     @property
#     def scroll_direction_label(self) -> str:
#         """Human-readable scroll direction."""
#         if not self._scroll_active:
#             return "None"
#         return "Up" if self._scroll_direction > 0 else "Down"

#     def left_click(self) -> None:
#         """Perform a single left click at current cursor position."""
#         pyautogui.click()

#     def right_click(self) -> None:
#         """Perform a right click at current cursor position."""
#         pyautogui.rightClick()

#     def double_click(self) -> None:
#         """Perform a double click at current cursor position."""
#         pyautogui.doubleClick()

#     def start_scroll(self, direction: str) -> None:
#         """
#         Start continuous scrolling.
        
#         Args:
#             direction: "up" or "down"
#         """
#         self._scroll_active = True
#         self._scroll_direction = cfg.SCROLL_SPEED if direction == "up" else -cfg.SCROLL_SPEED
#         self._last_scroll_time = 0.0

#     def stop_scroll(self) -> None:
#         """Stop continuous scrolling."""
#         self._scroll_active = False
#         self._scroll_direction = 0

#     def update_scroll(self) -> None:
#         """
#         Process one scroll tick if scrolling is active.
#         Called once per main loop frame. Uses time-based throttling
#         to maintain consistent scroll speed regardless of FPS.
#         """
#         if not self._scroll_active:
#             return

#         now = time.time()
#         if now - self._last_scroll_time >= cfg.SCROLL_INTERVAL:
#             pyautogui.scroll(self._scroll_direction)
#             self._last_scroll_time = now


"""
NeuroTouch OS — OS Automation Layer
=====================================
Handles all operating system interactions.
"""

import pyautogui
import time
import keyboard
import config as cfg


# ============================================================
# PYAUTOGUI SETTINGS
# ============================================================

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class OSAutomation:

    def __init__(self):

        self._scroll_active = False

        self._scroll_direction = 0

        self._last_scroll_time = 0.0

    # ============================================================
    # SCROLL STATUS
    # ============================================================

    @property
    def is_scrolling(self) -> bool:

        return self._scroll_active

    @property
    def scroll_direction_label(self) -> str:

        if not self._scroll_active:
            return "None"

        return (
            "Up"
            if self._scroll_direction > 0
            else "Down"
        )

    # ============================================================
    # MOUSE ACTIONS
    # ============================================================

    def left_click(self) -> None:

        pyautogui.click()

    def right_click(self) -> None:

        pyautogui.rightClick()

    def double_click(self) -> None:

        pyautogui.doubleClick()

    # ============================================================
    # WINDOW CONTROLS
    # ============================================================

    def minimize_window(self) -> None:

        keyboard.press_and_release(
            "windows+down"
        )

    def maximize_window(self) -> None:

        keyboard.press_and_release(
            "windows+up"
        )

    def close_window(self) -> None:

        keyboard.press_and_release(
            "alt+f4"
        )

    # ============================================================
    # SCROLLING
    # ============================================================

    def start_scroll(
        self,
        direction: str
    ) -> None:

        self._scroll_active = True

        if direction == "up":

            self._scroll_direction = (
                cfg.SCROLL_SPEED
            )

        else:

            self._scroll_direction = (
                -cfg.SCROLL_SPEED
            )

        self._last_scroll_time = 0.0

    def stop_scroll(self) -> None:

        self._scroll_active = False

        self._scroll_direction = 0

    def update_scroll(self) -> None:

        if not self._scroll_active:
            return

        now = time.time()

        if (
            now - self._last_scroll_time
            >= cfg.SCROLL_INTERVAL
        ):

            pyautogui.scroll(
                self._scroll_direction
            )

            self._last_scroll_time = now
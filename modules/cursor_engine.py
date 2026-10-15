"""
NeuroTouch OS — Cursor Engine
================================
OLD PROJECT STYLE CURSOR ENGINE
"""

import pyautogui
import numpy as np
from typing import Tuple
import config as cfg

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class CursorEngine:

    def __init__(self):

        self._prev_x = 0
        self._prev_y = 0

    def move(
        self,
        finger_x: int,
        finger_y: int,
        frame_width: int,
        frame_height: int
    ):

        # =====================================================
        # USE REAL FRAME SIZE
        # EXACTLY LIKE OLD PROJECT
        # =====================================================

        screen_x = np.interp(
            finger_x,
            (
                cfg.CURSOR_FRAME_MARGIN_X,
                frame_width - cfg.CURSOR_FRAME_MARGIN_X
            ),
            (
                0,
                cfg.SCREEN_WIDTH
            )
        )

        screen_y = np.interp(
            finger_y,
            (
                cfg.CURSOR_FRAME_MARGIN_Y,
                frame_height - cfg.CURSOR_FRAME_MARGIN_Y
            ),
            (
                0,
                cfg.SCREEN_HEIGHT
            )
        )

        # =====================================================
        # ORIGINAL SMOOTHING
        # =====================================================

        curr_x = self._prev_x + (
            screen_x - self._prev_x
        ) / cfg.CURSOR_SMOOTHING

        curr_y = self._prev_y + (
            screen_y - self._prev_y
        ) / cfg.CURSOR_SMOOTHING

        self._prev_x = curr_x
        self._prev_y = curr_y

        # =====================================================
        # EXACT OLD PROJECT CURSOR MOVE
        # =====================================================

        pyautogui.moveTo(curr_x, curr_y)

        return int(curr_x), int(curr_y)

    def get_position(self) -> Tuple[int, int]:

        return (
            int(self._prev_x),
            int(self._prev_y)
        )

    def reset(self):

        self._prev_x = 0
        self._prev_y = 0

    def jump_to(self, screen_x: int, screen_y: int):

        self._prev_x = screen_x
        self._prev_y = screen_y

        pyautogui.moveTo(
            screen_x,
            screen_y
        )
"""
NeuroTouch OS — Hand Tracking Module
======================================
Wraps MediaPipe Hands to detect and track hand landmarks.
Returns structured results with finger states and handedness.
"""

import mediapipe as mp
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple
import config as cfg


@dataclass
class HandData:
    """Structured hand detection result."""

    landmarks: list
    landmark_pixels: List[Tuple[int, int]]
    handedness: str
    fingers_up: List[bool] = field(
        default_factory=lambda: [False] * 5
    )
    num_fingers_up: int = 0


class HandTracker:
    """
    Real-time hand tracking using MediaPipe Hands.
    """

    def __init__(self):

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            max_num_hands=cfg.HAND_MAX_NUM_HANDS,
            model_complexity=cfg.HAND_MODEL_COMPLEXITY,
            min_detection_confidence=cfg.HAND_MIN_DETECTION_CONF,
            min_tracking_confidence=cfg.HAND_MIN_TRACKING_CONF,
        )

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

    def process(
        self,
        frame_rgb: np.ndarray,
        frame_width: int,
        frame_height: int
    ) -> List[HandData]:

        """
        Process RGB webcam frame and return detected hands.
        """

        results = self.hands.process(frame_rgb)

        hands_data = []

        if not results.multi_hand_landmarks:
            return hands_data

        for idx, hand_landmarks in enumerate(
            results.multi_hand_landmarks
        ):

            # =====================================================
            # HANDEDNESS
            # =====================================================

            handedness_label = (
                results.multi_handedness[idx]
                .classification[0]
                .label
            )

            # =====================================================
            # LANDMARK PIXELS
            # =====================================================

            landmark_pixels = []

            for lm in hand_landmarks.landmark:

                # ---------------------------------------------
                # SAFE NORMALIZED CLAMP
                # ---------------------------------------------

                safe_x = max(0.0, min(lm.x, 1.0))
                safe_y = max(0.0, min(lm.y, 1.0))

                px = int(safe_x * frame_width)
                py = int(safe_y * frame_height)

                # ---------------------------------------------
                # FINAL PIXEL CLAMP
                # ---------------------------------------------

                px = max(0, min(px, frame_width - 1))
                py = max(0, min(py, frame_height - 1))

                landmark_pixels.append((px, py))

            # =====================================================
            # FINGER STATES
            # =====================================================

            fingers_up = self._compute_fingers_up(
                landmark_pixels,
                handedness_label
            )

            num_fingers_up = sum(fingers_up)

            hand_data = HandData(
                landmarks=hand_landmarks,
                landmark_pixels=landmark_pixels,
                handedness=handedness_label,
                fingers_up=fingers_up,
                num_fingers_up=num_fingers_up,
            )

            hands_data.append(hand_data)

        return hands_data

    # =============================================================
    # FINGER DETECTION
    # =============================================================

    def _compute_fingers_up(
        self,
        lm: List[Tuple[int, int]],
        handedness: str
    ) -> List[bool]:

        fingers = [False] * 5

        # =====================================================
        # THUMB
        # =====================================================

        if handedness == "Right":
            fingers[0] = (
                lm[cfg.THUMB_TIP][0]
                < lm[cfg.THUMB_IP][0]
            )
        else:
            fingers[0] = (
                lm[cfg.THUMB_TIP][0]
                > lm[cfg.THUMB_IP][0]
            )

        # =====================================================
        # OTHER FINGERS
        # =====================================================

        fingers[1] = (
            lm[cfg.INDEX_FINGER_TIP][1]
            < lm[cfg.INDEX_FINGER_PIP][1]
        )

        fingers[2] = (
            lm[cfg.MIDDLE_FINGER_TIP][1]
            < lm[cfg.MIDDLE_FINGER_PIP][1]
        )

        fingers[3] = (
            lm[cfg.RING_FINGER_TIP][1]
            < lm[cfg.RING_FINGER_PIP][1]
        )

        fingers[4] = (
            lm[cfg.PINKY_FINGER_TIP][1]
            < lm[cfg.PINKY_FINGER_PIP][1]
        )

        return fingers

    # =============================================================
    # DRAW LANDMARKS
    # =============================================================

    def draw_landmarks(
        self,
        frame: np.ndarray,
        hand_data: HandData
    ) -> None:

        self.mp_draw.draw_landmarks(
            frame,
            hand_data.landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_draw_styles.get_default_hand_landmarks_style(),
            self.mp_draw_styles.get_default_hand_connections_style(),
        )

    # =============================================================
    # RELEASE
    # =============================================================

    def release(self) -> None:

        self.hands.close()
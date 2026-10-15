# # # # """
# # # # NeuroTouch OS — Gesture Recognition Engine
# # # # ============================================
# # # # Classifies hand gestures from landmark data.
# # # # Separates cursor-control gestures (right hand) from action gestures (left hand).
# # # # """

# # # # from enum import Enum, auto
# # # # from typing import List, Optional, Tuple
# # # # from modules.hand_tracker import HandData
# # # # import config as cfg
# # # # import math


# # # # class GestureType(Enum):
# # # #     """All recognized gesture types."""
# # # #     NONE = auto()
# # # #     CURSOR_MOVE = auto()       # Right hand: index finger tracking
# # # #     HOVER_ON = auto()          # Left hand: open palm (>=4 fingers)
# # # #     HOVER_OFF = auto()         # Left hand: closed fist or removed
# # # #     RIGHT_CLICK = auto()       # Left hand: peace sign (index + middle only)
# # # #     DOUBLE_CLICK = auto()      # Left hand: thumbs up (thumb only)


# # # # class GestureResult:
# # # #     """Result of gesture classification for a single frame."""

# # # #     def __init__(self):
# # # #         self.gesture: GestureType = GestureType.NONE
# # # #         self.cursor_target: Optional[Tuple[int, int]] = None  # (x, y) for cursor
# # # #         self.confidence: float = 0.0
# # # #         self.hand_label: str = ""


# # # # class GestureEngine:
# # # #     """
# # # #     Classifies gestures from hand tracking data.
    
# # # #     Architecture:
# # # #     - RIGHT hand (MediaPipe label "Right" = user's left in flipped view):
# # # #       hover toggle, right click, double click
# # # #     - LEFT hand (MediaPipe label "Left" = user's right in flipped view):
# # # #       cursor movement only
      
# # # #     Hover mode is a TOGGLE — show open palm once to turn ON,
# # # #     show open palm again to turn OFF. Persists after hand removal.
# # # #     """

# # # #     def __init__(self):
# # # #         self._hover_active = False
# # # #         self._palm_was_open = False  # Track palm state for edge detection
# # # #         self._last_hover_toggle_time = 0.0  # Cooldown for hover toggle

# # # #     @property
# # # #     def hover_active(self) -> bool:
# # # #         """Whether hover mode is currently active."""
# # # #         return self._hover_active

# # # #     @hover_active.setter
# # # #     def hover_active(self, value: bool):
# # # #         self._hover_active = value

# # # #     def classify(self, hands: List[HandData], frame_width: int, frame_height: int) -> List[GestureResult]:
# # # #         """
# # # #         Classify gestures from all detected hands.
        
# # # #         Args:
# # # #             hands: List of HandData from hand tracker
# # # #             frame_width: Camera frame width
# # # #             frame_height: Camera frame height
            
# # # #         Returns:
# # # #             List of GestureResult objects
# # # #         """
# # # #         results = []
# # # #         left_hand_found = False

# # # #         for hand in hands:
# # # #             # MediaPipe labels in flipped/selfie view are INVERTED:
# # # #             # "Right" label = user's actual LEFT hand (after cv2.flip)
# # # #             # "Left" label = user's actual RIGHT hand (after cv2.flip)
# # # #             #
# # # #             # RELIABILITY FIX: When only one hand is in frame, MediaPipe
# # # #             # handedness confidence drops. Use wrist X-position as a
# # # #             # secondary check: wrist on the LEFT half of the flipped frame
# # # #             # = user's physical right hand (cursor hand), regardless of label.
# # # #             wrist_x = hand.landmark_pixels[0][0]  # landmark 0 = wrist
# # # #             physically_right_hand = wrist_x < frame_width * 0.55

# # # #             is_action_hand = (hand.handedness == "Right") and not physically_right_hand
# # # #             is_cursor_hand = (hand.handedness == "Left") or physically_right_hand

# # # #             if is_action_hand:
# # # #                 # User's LEFT hand → action gestures (hover, right-click, double-click)
# # # #                 left_hand_found = True
# # # #                 result = self._classify_left_hand(hand)
# # # #                 if result:
# # # #                     results.append(result)
# # # #             elif is_cursor_hand:
# # # #                 # User's RIGHT hand → cursor movement only
# # # #                 result = self._classify_right_hand(hand, frame_width, frame_height)
# # # #                 if result:
# # # #                     results.append(result)

# # # #         # If left hand is not visible, reset palm-open tracker
# # # #         # (so next time palm appears, it can trigger a toggle)
# # # #         if not left_hand_found:
# # # #             self._palm_was_open = False

# # # #         return results

# # # #     def _classify_left_hand(self, hand: HandData) -> Optional[GestureResult]:
# # # #         """
# # # #         Classify gestures from the user's LEFT hand.
        
# # # #         Priority order (checked first wins):
# # # #         1. Open palm (≥4 fingers) → TOGGLE hover ON/OFF (edge-triggered)
# # # #         2. Peace sign (index + middle only) → Right Click
# # # #         3. Thumbs up (thumb only) → Double Click
        
# # # #         Args:
# # # #             hand: HandData for the left hand
            
# # # #         Returns:
# # # #             GestureResult or None
# # # #         """
# # # #         import time

# # # #         fingers = hand.fingers_up
# # # #         num_up = hand.num_fingers_up
# # # #         result = GestureResult()
# # # #         result.hand_label = "Left"

# # # #         # 1. Open Palm → TOGGLE hover mode (edge-triggered with cooldown)
# # # #         palm_is_open = num_up >= cfg.PALM_OPEN_MIN_FINGERS

# # # #         if palm_is_open and not self._palm_was_open:
# # # #             # Palm just opened (rising edge) — check cooldown
# # # #             now = time.time()
# # # #             if now - self._last_hover_toggle_time >= cfg.COOLDOWN_HOVER_TOGGLE:
# # # #                 self._last_hover_toggle_time = now
# # # #                 self._hover_active = not self._hover_active  # TOGGLE
# # # #                 result.gesture = GestureType.HOVER_ON if self._hover_active else GestureType.HOVER_OFF
# # # #                 self._palm_was_open = True
# # # #                 return result

# # # #         self._palm_was_open = palm_is_open

# # # #         # Don't process other gestures if palm is open (prevents conflicts)
# # # #         if palm_is_open:
# # # #             return None

# # # #         # 2. Peace Sign → Right Click
# # # #         # Index and middle up, thumb/ring/pinky down
# # # #         if (fingers[1] and fingers[2] and
# # # #                 not fingers[3] and not fingers[4]):
# # # #             result.gesture = GestureType.RIGHT_CLICK
# # # #             return result

# # # #         # 3. Thumbs Up → Double Click
# # # #         # Only thumb is up, all other fingers down
# # # #         if (fingers[0] and not fingers[1] and
# # # #                 not fingers[2] and not fingers[3] and not fingers[4]):
# # # #             result.gesture = GestureType.DOUBLE_CLICK
# # # #             return result

# # # #         return None

# # # #     def _classify_right_hand(self, hand: HandData, fw: int, fh: int) -> Optional[GestureResult]:
# # # #         """
# # # #         Classify gestures from the user's RIGHT hand.
        
# # # #         Cursor movement is ALWAYS active when the right hand is visible —
# # # #         it does NOT require any specific finger pose. The index fingertip
# # # #         position is used as the cursor target unconditionally.
        
# # # #         This ensures cursor movement persists after the left hand is removed
# # # #         and is never gated by palm/gesture state.
        
# # # #         Args:
# # # #             hand: HandData for the right hand
# # # #             fw: Frame width
# # # #             fh: Frame height
            
# # # #         Returns:
# # # #             GestureResult with CURSOR_MOVE, always (hand must be visible)
# # # #         """
# # # #         lm = hand.landmark_pixels
# # # #         result = GestureResult()
# # # #         result.hand_label = "Right"

# # # #         # Always emit CURSOR_MOVE using index fingertip.
# # # #         # No finger-pose check — cursor tracks the hand whenever it's detected.
# # # #         index_tip = lm[cfg.INDEX_FINGER_TIP]
# # # #         result.gesture = GestureType.CURSOR_MOVE
# # # #         result.cursor_target = index_tip
# # # #         return result






# # # """
# # # NeuroTouch OS — Gesture Recognition Engine
# # # ============================================
# # # Classifies hand gestures from landmark data.
# # # Separates cursor-control gestures (right hand) from action gestures (left hand).
# # # """

# # # from enum import Enum, auto
# # # from typing import List, Optional, Tuple
# # # from modules.hand_tracker import HandData
# # # import config as cfg
# # # import math
# # # import time


# # # class GestureType(Enum):
# # #     """All recognized gesture types."""
# # #     NONE = auto()
# # #     CURSOR_MOVE = auto()
# # #     HOVER_ON = auto()
# # #     HOVER_OFF = auto()
# # #     RIGHT_CLICK = auto()
# # #     DOUBLE_CLICK = auto()


# # # class GestureResult:
# # #     """Result of gesture classification for a single frame."""

# # #     def __init__(self):
# # #         self.gesture: GestureType = GestureType.NONE
# # #         self.cursor_target: Optional[Tuple[int, int]] = None
# # #         self.confidence: float = 0.0
# # #         self.hand_label: str = ""


# # # class GestureEngine:
# # #     """
# # #     Gesture Engine
    
# # #     LEFT HAND:
# # #     - Open Palm → Toggle Hover ON/OFF
    
# # #     RIGHT HAND:
# # #     - Index finger → Cursor movement
    
# # #     Hover persists even after removing the left hand.
# # #     """

# # #     def __init__(self):

# # #         # Hover state
# # #         self._hover_active = False

# # #         # Palm edge detection
# # #         self._palm_was_open = False

# # #         # Toggle cooldown
# # #         self._last_hover_toggle_time = 0.0

# # #     @property
# # #     def hover_active(self) -> bool:
# # #         return self._hover_active

# # #     @hover_active.setter
# # #     def hover_active(self, value: bool):
# # #         self._hover_active = value

# # #     def classify(
# # #         self,
# # #         hands: List[HandData],
# # #         frame_width: int,
# # #         frame_height: int
# # #     ) -> List[GestureResult]:

# # #         results = []
# # #         left_hand_found = False

# # #         for hand in hands:

# # #             # =====================================================
# # #             # STABLE HANDEDNESS DETECTION
# # #             # =====================================================
# # #             # After cv2.flip():
# # #             #
# # #             # MediaPipe "Left"
# # #             # = user's RIGHT hand
# # #             # = cursor hand
# # #             #
# # #             # MediaPipe "Right"
# # #             # = user's LEFT hand
# # #             # = action hand
# # #             # =====================================================

# # #             is_action_hand = hand.handedness == "Right"
# # #             is_cursor_hand = hand.handedness == "Left"

# # #             # =====================================================
# # #             # LEFT HAND → HOVER TOGGLE
# # #             # =====================================================

# # #             if is_action_hand:

# # #                 left_hand_found = True

# # #                 result = self._classify_left_hand(hand)

# # #                 if result:
# # #                     results.append(result)

# # #             # =====================================================
# # #             # RIGHT HAND → CURSOR
# # #             # =====================================================

# # #             elif is_cursor_hand:

# # #                 result = self._classify_right_hand(
# # #                     hand,
# # #                     frame_width,
# # #                     frame_height
# # #                 )

# # #                 if result:
# # #                     results.append(result)

# # #         # Reset palm edge detector if left hand disappears
# # #         if not left_hand_found:
# # #             self._palm_was_open = False

# # #         return results

# # #     # =============================================================
# # #     # LEFT HAND GESTURES
# # #     # =============================================================

# # #     def _classify_left_hand(
# # #         self,
# # #         hand: HandData
# # #     ) -> Optional[GestureResult]:

# # #         fingers = hand.fingers_up
# # #         num_up = hand.num_fingers_up

# # #         result = GestureResult()
# # #         result.hand_label = "Left"

# # #         # =========================================================
# # #         # OPEN PALM → TOGGLE HOVER
# # #         # =========================================================

# # #         palm_is_open = num_up >= cfg.PALM_OPEN_MIN_FINGERS

# # #         if palm_is_open and not self._palm_was_open:

# # #             now = time.time()

# # #             if now - self._last_hover_toggle_time >= cfg.COOLDOWN_HOVER_TOGGLE:

# # #                 self._last_hover_toggle_time = now

# # #                 # TOGGLE
# # #                 self._hover_active = not self._hover_active

# # #                 if self._hover_active:
# # #                     result.gesture = GestureType.HOVER_ON
# # #                 else:
# # #                     result.gesture = GestureType.HOVER_OFF

# # #                 self._palm_was_open = True

# # #                 return result

# # #         self._palm_was_open = palm_is_open

# # #         return None

# # #     # =============================================================
# # #     # RIGHT HAND CURSOR CONTROL
# # #     # =============================================================

# # #     def _classify_right_hand(
# # #         self,
# # #         hand: HandData,
# # #         fw: int,
# # #         fh: int
# # #     ) -> Optional[GestureResult]:

# # #         # Cursor only works when hover mode is ON
# # #         if not self._hover_active:
# # #             return None

# # #         lm = hand.landmark_pixels

# # #         result = GestureResult()
# # #         result.hand_label = "Right"

# # #         # Index fingertip
# # #         index_tip = lm[cfg.INDEX_FINGER_TIP]

# # #         result.gesture = GestureType.CURSOR_MOVE
# # #         result.cursor_target = index_tip

# # #         return result

# # """
# # NeuroTouch OS — Gesture Recognition Engine
# # ============================================
# # Handles:
# # - Cursor movement
# # - Hover toggle
# # - Right click
# # - Double click
# # """

# # from enum import Enum, auto
# # from typing import List, Optional, Tuple
# # from modules.hand_tracker import HandData
# # import config as cfg
# # import time


# # # ============================================================
# # # GESTURE TYPES
# # # ============================================================

# # class GestureType(Enum):

# #     NONE = auto()

# #     CURSOR_MOVE = auto()

# #     HOVER_ON = auto()

# #     HOVER_OFF = auto()

# #     RIGHT_CLICK = auto()

# #     DOUBLE_CLICK = auto()


# # # ============================================================
# # # RESULT OBJECT
# # # ============================================================

# # class GestureResult:

# #     def __init__(self):

# #         self.gesture: GestureType = GestureType.NONE

# #         self.cursor_target: Optional[Tuple[int, int]] = None

# #         self.confidence: float = 0.0

# #         self.hand_label: str = ""


# # # ============================================================
# # # GESTURE ENGINE
# # # ============================================================

# # class GestureEngine:

# #     def __init__(self):

# #         # Hover state
# #         self._hover_active = False

# #         # Palm detection memory
# #         self._palm_was_open = False

# #         # Cooldown timer
# #         self._last_hover_toggle_time = 0.0

# #     # ========================================================
# #     # PROPERTY
# #     # ========================================================

# #     @property
# #     def hover_active(self) -> bool:
# #         return self._hover_active

# #     @hover_active.setter
# #     def hover_active(self, value: bool):
# #         self._hover_active = value

# #     # ========================================================
# #     # MAIN CLASSIFIER
# #     # ========================================================

# #     def classify(
# #         self,
# #         hands: List[HandData],
# #         frame_width: int,
# #         frame_height: int
# #     ) -> List[GestureResult]:

# #         results = []

# #         left_hand_found = False

# #         for hand in hands:

# #             # ------------------------------------------------
# #             # ACTION HAND
# #             # ------------------------------------------------

# #             # MediaPipe mirrored logic
# #             # "Right" = user's LEFT hand
# #             is_action_hand = (
# #                 hand.handedness == "Right"
# #             )

# #             # ------------------------------------------------
# #             # HOVER TOGGLE
# #             # ------------------------------------------------

# #             if is_action_hand:

# #                 left_hand_found = True

# #                 action_result = self._classify_left_hand(
# #                     hand
# #                 )

# #                 if action_result:
# #                     results.append(action_result)

# #             # ------------------------------------------------
# #             # CURSOR HAND
# #             # ------------------------------------------------

# #             cursor_result = self._classify_cursor_hand(
# #                 hand,
# #                 frame_width,
# #                 frame_height
# #             )

# #             if cursor_result:
# #                 results.append(cursor_result)

# #         # Reset palm memory
# #         if not left_hand_found:
# #             self._palm_was_open = False

# #         return results

# #     # ========================================================
# #     # LEFT HAND GESTURES
# #     # ========================================================

# #     def _classify_left_hand(
# #         self,
# #         hand: HandData
# #     ) -> Optional[GestureResult]:

# #         num_up = hand.num_fingers_up

# #         result = GestureResult()

# #         result.hand_label = "Left"

# #         # ----------------------------------------------------
# #         # OPEN PALM
# #         # ----------------------------------------------------

# #         palm_is_open = (
# #             num_up >= cfg.PALM_OPEN_MIN_FINGERS
# #         )

# #         if (
# #             palm_is_open
# #             and not self._palm_was_open
# #         ):

# #             now = time.time()

# #             if (
# #                 now - self._last_hover_toggle_time
# #                 >= cfg.COOLDOWN_HOVER_TOGGLE
# #             ):

# #                 self._last_hover_toggle_time = now

# #                 # Toggle hover
# #                 self._hover_active = (
# #                     not self._hover_active
# #                 )

# #                 if self._hover_active:
# #                     result.gesture = GestureType.HOVER_ON
# #                 else:
# #                     result.gesture = GestureType.HOVER_OFF

# #                 self._palm_was_open = True

# #                 return result

# #         self._palm_was_open = palm_is_open

# #         return None

# #     # ========================================================
# #     # CURSOR CONTROL
# #     # ========================================================

# #     def _classify_cursor_hand(
# #         self,
# #         hand: HandData,
# #         fw: int,
# #         fh: int
# #     ) -> Optional[GestureResult]:

# #         # Hover must be active
# #         if not self._hover_active:
# #             return None

# #         lm = hand.landmark_pixels

# #         result = GestureResult()

# #         result.hand_label = hand.handedness

# #         # ----------------------------------------------------
# #         # INDEX FINGER
# #         # ----------------------------------------------------

# #         index_tip = lm[cfg.INDEX_FINGER_TIP]

# #         x, y = index_tip

# #         # ----------------------------------------------------
# #         # SAFE CLAMP
# #         # ----------------------------------------------------

# #         x = max(0, min(x, fw - 1))
# #         y = max(0, min(y, fh - 1))

# #         # ----------------------------------------------------
# #         # CURSOR MOVE
# #         # ----------------------------------------------------

# #         result.gesture = GestureType.CURSOR_MOVE

# #         result.cursor_target = (x, y)

# #         return result



# """
# NeuroTouch OS — Gesture Recognition Engine
# ============================================
# ✋ Open Palm (3 sec hold) → Hover ON/OFF
# 👍 Thumbs Up → Double Click
# """

# from enum import Enum, auto
# from typing import List, Optional, Tuple
# from modules.hand_tracker import HandData
# import config as cfg
# import time


# # ============================================================
# # GESTURE TYPES
# # ============================================================

# class GestureType(Enum):

#     NONE = auto()

#     HOVER_ON = auto()

#     HOVER_OFF = auto()

    


# # ============================================================
# # RESULT OBJECT
# # ============================================================

# class GestureResult:

#     def __init__(self):

#         self.gesture: GestureType = GestureType.NONE

#         self.cursor_target: Optional[Tuple[int, int]] = None

#         self.hand_label: str = ""


# # ============================================================
# # GESTURE ENGINE
# # ============================================================

# class GestureEngine:

#     def __init__(self):

#         # Hover state
#         self._hover_active = False

#         # Palm hold timer
#         self._palm_start_time = None

#         # Prevent repeated trigger
#         self._palm_triggered = False

#         # Cooldown
#         self._last_toggle_time = 0.0

#     @property
#     def hover_active(self):

#         return self._hover_active

#     # ============================================================
#     # MAIN CLASSIFIER
#     # ============================================================

#     def classify(
#         self,
#         hands: List[HandData],
#         frame_width: int,
#         frame_height: int
#     ):

#         results = []

#         # ========================================================
#         # ✋ OPEN PALM → TOGGLE HOVER
#         # HOLD FOR 3 SECONDS
#         # ========================================================

#         palm_detected = False

#         for hand in hands:

#             lm = hand.landmark_pixels

#             thumb_tip = lm[cfg.THUMB_TIP]
#             thumb_ip = lm[cfg.THUMB_IP]

#             index_tip = lm[cfg.INDEX_FINGER_TIP]
#             index_pip = lm[cfg.INDEX_FINGER_PIP]

#             middle_tip = lm[cfg.MIDDLE_FINGER_TIP]
#             middle_pip = lm[cfg.MIDDLE_FINGER_PIP]

#             ring_tip = lm[cfg.RING_FINGER_TIP]
#             ring_pip = lm[cfg.RING_FINGER_PIP]

#             pinky_tip = lm[cfg.PINKY_FINGER_TIP]
#             pinky_pip = lm[cfg.PINKY_FINGER_PIP]

#             # ====================================================
#             # ✋ OPEN PALM
#             # ====================================================

#             palm_open = (
#                 index_tip[1] < index_pip[1]
#                 and middle_tip[1] < middle_pip[1]
#                 and ring_tip[1] < ring_pip[1]
#                 and pinky_tip[1] < pinky_pip[1]
#             )

#             if palm_open:

#                 palm_detected = True

#                 if self._palm_start_time is None:

#                     self._palm_start_time = time.time()

#                 hold_time = (
#                     time.time() - self._palm_start_time
#                 )

#                 if (
#                     hold_time >= 3
#                     and not self._palm_triggered
#                     and time.time() - self._last_toggle_time > 1.5
#                 ):

#                     self._last_toggle_time = time.time()

#                     self._hover_active = (
#                         not self._hover_active
#                     )

#                     result = GestureResult()

#                     if self._hover_active:

#                         result.gesture = GestureType.HOVER_ON

#                     else:

#                         result.gesture = GestureType.HOVER_OFF

#                     results.append(result)

#                     self._palm_triggered = True

           

#         # ========================================================
#         # RESET PALM TIMER
#         # ========================================================

#         if not palm_detected:

#             self._palm_start_time = None

#             self._palm_triggered = False

#         return results

"""
NeuroTouch OS — Gesture Recognition Engine
============================================
✋ Open Palm (3 sec hold) → Hover ON/OFF
👍 Thumbs Up → Double Click
"""

from enum import Enum, auto
from typing import List, Optional, Tuple
from modules.hand_tracker import HandData
import config as cfg
import time


# ============================================================
# GESTURE TYPES
# ============================================================

class GestureType(Enum):

    NONE = auto()

    HOVER_ON = auto()

    HOVER_OFF = auto()

    DOUBLE_CLICK = auto()


# ============================================================
# RESULT OBJECT
# ============================================================

class GestureResult:

    def __init__(self):

        self.gesture: GestureType = GestureType.NONE

        self.cursor_target: Optional[Tuple[int, int]] = None

        self.hand_label: str = ""


# ============================================================
# GESTURE ENGINE
# ============================================================

class GestureEngine:

    def __init__(self):

        # Hover state
        self._hover_active = False

        # Palm hold timer
        self._palm_start_time = None

        # Prevent repeated trigger
        self._palm_triggered = False

        # Double click cooldown
        self._last_double_click = 0

        # Cooldown
        self._last_toggle_time = 0.0

    @property
    def hover_active(self):

        return self._hover_active

    # ============================================================
    # MAIN CLASSIFIER
    # ============================================================

    def classify(
        self,
        hands: List[HandData],
        frame_width: int,
        frame_height: int
    ):

        results = []

        # ========================================================
        # ✋ OPEN PALM → TOGGLE HOVER
        # ========================================================

        palm_detected = False

        for hand in hands:

            lm = hand.landmark_pixels

            thumb_tip = lm[cfg.THUMB_TIP]
            thumb_ip = lm[cfg.THUMB_IP]

            index_tip = lm[cfg.INDEX_FINGER_TIP]
            index_pip = lm[cfg.INDEX_FINGER_PIP]

            middle_tip = lm[cfg.MIDDLE_FINGER_TIP]
            middle_pip = lm[cfg.MIDDLE_FINGER_PIP]

            ring_tip = lm[cfg.RING_FINGER_TIP]
            ring_pip = lm[cfg.RING_FINGER_PIP]

            pinky_tip = lm[cfg.PINKY_FINGER_TIP]
            pinky_pip = lm[cfg.PINKY_FINGER_PIP]

            # ====================================================
            # ✋ OPEN PALM
            # ====================================================

            palm_open = (
                index_tip[1] < index_pip[1]
                and middle_tip[1] < middle_pip[1]
                and ring_tip[1] < ring_pip[1]
                and pinky_tip[1] < pinky_pip[1]
            )

            if palm_open:

                palm_detected = True

                if self._palm_start_time is None:

                    self._palm_start_time = time.time()

                hold_time = (
                    time.time() - self._palm_start_time
                )

                if (
                    hold_time >= 3
                    and not self._palm_triggered
                    and time.time() - self._last_toggle_time > 1.5
                ):

                    self._last_toggle_time = time.time()

                    self._hover_active = (
                        not self._hover_active
                    )

                    result = GestureResult()

                    if self._hover_active:

                        result.gesture = GestureType.HOVER_ON

                    else:

                        result.gesture = GestureType.HOVER_OFF

                    results.append(result)

                    self._palm_triggered = True

            # ====================================================
            # 👍 THUMBS UP → DOUBLE CLICK
            # ====================================================

            thumbs_up = (

                thumb_tip[1] < thumb_ip[1]

                and index_tip[1] > index_pip[1]

                and middle_tip[1] > middle_pip[1]

                and ring_tip[1] > ring_pip[1]

                and pinky_tip[1] > pinky_pip[1]
            )

            if thumbs_up:

                if (
                    time.time() - self._last_double_click
                    > 2
                ):

                    result = GestureResult()

                    result.gesture = (
                        GestureType.DOUBLE_CLICK
                    )

                    results.append(result)

                    self._last_double_click = (
                        time.time()
                    )

        # ========================================================
        # RESET PALM TIMER
        # ========================================================

        if not palm_detected:

            self._palm_start_time = None

            self._palm_triggered = False

        return results
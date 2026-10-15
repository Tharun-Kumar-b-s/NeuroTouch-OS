# # """
# # NeuroTouch OS — Face Detection Module
# # =======================================
# # Wraps MediaPipe FaceMesh for eye-state detection.
# # Computes Eye Aspect Ratio (EAR) for drowsiness monitoring.
# # """

# # import mediapipe as mp
# # import numpy as np
# # from typing import Optional, Tuple
# # import config as cfg


# # class FaceDetector:
# #     """
# #     Real-time face landmark detection using MediaPipe FaceMesh.
    
# #     Primary purpose: compute Eye Aspect Ratio (EAR) for drowsiness
# #     detection. Uses refined landmarks for accurate iris tracking.
# #     """

# #     def __init__(self):
# #         self.mp_face_mesh = mp.solutions.face_mesh
# #         self.face_mesh = self.mp_face_mesh.FaceMesh(
# #             max_num_faces=cfg.FACE_MAX_NUM_FACES,
# #             refine_landmarks=cfg.FACE_REFINE_LANDMARKS,
# #             min_detection_confidence=cfg.FACE_MIN_DETECTION_CONF,
# #             min_tracking_confidence=cfg.FACE_MIN_TRACKING_CONF,
# #         )
# #         self._last_ear = None  # Cache last EAR for skipped frames

# #     def process(self, frame_rgb: np.ndarray, frame_width: int, frame_height: int) -> Optional[float]:
# #         """
# #         Process a single RGB frame and compute average Eye Aspect Ratio.
        
# #         Args:
# #             frame_rgb: RGB frame from webcam
# #             frame_width: Frame width in pixels
# #             frame_height: Frame height in pixels
            
# #         Returns:
# #             Average EAR (float) or None if no face detected
# #         """
# #         results = self.face_mesh.process(frame_rgb)

# #         if not results.multi_face_landmarks:
# #             self._last_ear = None
# #             return None

# #         face_landmarks = results.multi_face_landmarks[0]

# #         # Convert to pixel coordinates for EAR calculation
# #         landmarks_px = []
# #         for lm in face_landmarks.landmark:
# #             landmarks_px.append((
# #                 int(lm.x * frame_width),
# #                 int(lm.y * frame_height),
# #             ))

# #         # Compute EAR for both eyes
# #         left_ear = self._compute_ear(landmarks_px, cfg.LEFT_EYE)
# #         right_ear = self._compute_ear(landmarks_px, cfg.RIGHT_EYE)

# #         # Average of both eyes
# #         avg_ear = (left_ear + right_ear) / 2.0
# #         self._last_ear = avg_ear
# #         return avg_ear

# #     def get_cached_ear(self) -> Optional[float]:
# #         """Return the last computed EAR (for skipped frames)."""
# #         return self._last_ear

# #     @staticmethod
# #     def _compute_ear(landmarks: list, eye_indices: list) -> float:
# #         """
# #         Compute Eye Aspect Ratio (EAR) for one eye.
        
# #         EAR = (|p2 - p6| + |p3 - p5|) / (2 * |p1 - p4|)
        
# #         Where p1-p6 are the 6 eye landmarks in order:
# #         p1 = outer corner, p2 = upper-outer, p3 = upper-inner,
# #         p4 = inner corner, p5 = lower-inner, p6 = lower-outer
        
# #         Args:
# #             landmarks: All face landmarks in pixel coords
# #             eye_indices: 6 landmark indices for the eye
            
# #         Returns:
# #             EAR value (float). ~0.3 when open, ~0.05 when closed
# #         """
# #         p1 = np.array(landmarks[eye_indices[0]])  # Outer corner
# #         p2 = np.array(landmarks[eye_indices[1]])  # Upper outer
# #         p3 = np.array(landmarks[eye_indices[2]])  # Upper inner
# #         p4 = np.array(landmarks[eye_indices[3]])  # Inner corner
# #         p5 = np.array(landmarks[eye_indices[4]])  # Lower inner
# #         p6 = np.array(landmarks[eye_indices[5]])  # Lower outer

# #         # Vertical distances
# #         vertical_1 = np.linalg.norm(p2 - p6)
# #         vertical_2 = np.linalg.norm(p3 - p5)

# #         # Horizontal distance
# #         horizontal = np.linalg.norm(p1 - p4)

# #         # Avoid division by zero
# #         if horizontal == 0:
# #             return 0.0

# #         ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
# #         return ear

# #     def release(self) -> None:
# #         """Release MediaPipe resources."""
# #         self.face_mesh.close()

# """
# NeuroTouch OS — Face Detection Module
# =======================================
# Eye Gesture + EAR Detection
# """

# import mediapipe as mp
# import numpy as np
# import time
# import subprocess
# import os
# from typing import Optional
# import config as cfg


# class FaceDetector:

#     def __init__(self):

#         self.mp_face_mesh = mp.solutions.face_mesh

#         self.face_mesh = self.mp_face_mesh.FaceMesh(
#             max_num_faces=cfg.FACE_MAX_NUM_FACES,
#             refine_landmarks=cfg.FACE_REFINE_LANDMARKS,
#             min_detection_confidence=cfg.FACE_MIN_DETECTION_CONF,
#             min_tracking_confidence=cfg.FACE_MIN_TRACKING_CONF,
#         )

#         self._last_ear = None

#         # =====================================================
#         # EYE GESTURE TIMERS
#         # =====================================================

#         self.left_wink_start = None
#         self.right_wink_start = None
#         self.both_eye_start = None

#         self.cooldown_time = 3
#         self.last_trigger_time = 0

#     def process(
#         self,
#         frame_rgb: np.ndarray,
#         frame_width: int,
#         frame_height: int
#     ) -> Optional[float]:

#         results = self.face_mesh.process(frame_rgb)

#         if not results.multi_face_landmarks:
#             self._last_ear = None
#             return None

#         face_landmarks = results.multi_face_landmarks[0]

#         landmarks_px = []

#         for lm in face_landmarks.landmark:

#             landmarks_px.append((
#                 int(lm.x * frame_width),
#                 int(lm.y * frame_height),
#             ))

#         # =====================================================
#         # EYE ASPECT RATIOS
#         # =====================================================

#         left_ear = self._compute_ear(
#             landmarks_px,
#             cfg.LEFT_EYE
#         )

#         right_ear = self._compute_ear(
#             landmarks_px,
#             cfg.RIGHT_EYE
#         )

#         avg_ear = (left_ear + right_ear) / 2.0

#         self._last_ear = avg_ear

#         # =====================================================
#         # EYE GESTURE SYSTEM
#         # =====================================================

#         now = time.time()

#         if now - self.last_trigger_time > self.cooldown_time:

#             LEFT_CLOSED = left_ear < 0.18
#             RIGHT_CLOSED = right_ear < 0.18

#             # =================================================
#             # LEFT WINK → CHROME
#             # =================================================

#             if LEFT_CLOSED and not RIGHT_CLOSED:

#                 if self.left_wink_start is None:
#                     self.left_wink_start = now

#                 elif now - self.left_wink_start > 2:

#                     print("[EYE] LEFT WINK → CHROME")

#                     subprocess.Popen("start chrome", shell=True)

#                     self.last_trigger_time = now
#                     self.left_wink_start = None

#             else:
#                 self.left_wink_start = None

#             # =================================================
#             # RIGHT WINK → FILE EXPLORER
#             # =================================================

#             if RIGHT_CLOSED and not LEFT_CLOSED:

#                 if self.right_wink_start is None:
#                     self.right_wink_start = now

#                 elif now - self.right_wink_start > 2:

#                     print("[EYE] RIGHT WINK → FILE EXPLORER")

#                     subprocess.Popen("explorer")

#                     self.last_trigger_time = now
#                     self.right_wink_start = None

#             else:
#                 self.right_wink_start = None

#             # =================================================
#             # BOTH EYES CLOSED → WHATSAPP
#             # =================================================

#             if LEFT_CLOSED and RIGHT_CLOSED:

#                 if self.both_eye_start is None:
#                     self.both_eye_start = now

#                 elif now - self.both_eye_start > 2:

#                     print("[EYE] BOTH EYES → WHATSAPP")

#                     try:

#                         subprocess.Popen(
#                             "start whatsapp:",
#                             shell=True
#                         )

#                     except Exception as e:

#                         print("[ERROR] WhatsApp launch failed:", e)

#                     self.last_trigger_time = now
#                     self.both_eye_start = None

#             else:
#                 self.both_eye_start = None

#         return avg_ear

#     def get_cached_ear(self) -> Optional[float]:

#         return self._last_ear

#     @staticmethod
#     def _compute_ear(
#         landmarks: list,
#         eye_indices: list
#     ) -> float:

#         p1 = np.array(landmarks[eye_indices[0]])
#         p2 = np.array(landmarks[eye_indices[1]])
#         p3 = np.array(landmarks[eye_indices[2]])
#         p4 = np.array(landmarks[eye_indices[3]])
#         p5 = np.array(landmarks[eye_indices[4]])
#         p6 = np.array(landmarks[eye_indices[5]])

#         vertical_1 = np.linalg.norm(p2 - p6)
#         vertical_2 = np.linalg.norm(p3 - p5)

#         horizontal = np.linalg.norm(p1 - p4)

#         if horizontal == 0:
#             return 0.0

#         ear = (
#             vertical_1 + vertical_2
#         ) / (2.0 * horizontal)

#         return ear

#     def release(self) -> None:

#         self.face_mesh.close()

"""
NeuroTouch OS — Face Detection Module
=======================================
Eye Gesture + EAR Detection
"""

import mediapipe as mp
import numpy as np
import time
import subprocess
from typing import Optional
import config as cfg


class FaceDetector:

    def __init__(self):

        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=cfg.FACE_MAX_NUM_FACES,
            refine_landmarks=cfg.FACE_REFINE_LANDMARKS,
            min_detection_confidence=cfg.FACE_MIN_DETECTION_CONF,
            min_tracking_confidence=cfg.FACE_MIN_TRACKING_CONF,
        )

        self._last_ear = None

        # =====================================================
        # EYE GESTURE TIMERS
        # =====================================================

        self.left_wink_start = None
        self.right_wink_start = None
        self.both_eye_start = None

        self.cooldown_time = 3
        self.last_trigger_time = 0

    def process(
        self,
        frame_rgb: np.ndarray,
        frame_width: int,
        frame_height: int
    ) -> Optional[float]:

        results = self.face_mesh.process(frame_rgb)

        if not results.multi_face_landmarks:

            self._last_ear = None

            return None

        face_landmarks = results.multi_face_landmarks[0]

        landmarks_px = []

        for lm in face_landmarks.landmark:

            landmarks_px.append((
                int(lm.x * frame_width),
                int(lm.y * frame_height),
            ))

        # =====================================================
        # EYE ASPECT RATIOS
        # =====================================================

        left_ear = self._compute_ear(
            landmarks_px,
            cfg.LEFT_EYE
        )

        right_ear = self._compute_ear(
            landmarks_px,
            cfg.RIGHT_EYE
        )

        avg_ear = (
            left_ear + right_ear
        ) / 2.0

        self._last_ear = avg_ear

        # =====================================================
        # EYE GESTURE SYSTEM
        # =====================================================

        now = time.time()

        if (
            now - self.last_trigger_time
            > self.cooldown_time
        ):

            LEFT_CLOSED = left_ear < 0.18
            RIGHT_CLOSED = right_ear < 0.18

            # =================================================
            # LEFT WINK → CHROME
            # =================================================

            if (
                LEFT_CLOSED
                and not RIGHT_CLOSED
            ):

                if self.left_wink_start is None:

                    self.left_wink_start = now

                elif (
                    now - self.left_wink_start
                    > 2
                ):

                    print(
                        "[EYE] LEFT WINK → CHROME"
                    )

                    subprocess.Popen(
                        "start chrome",
                        shell=True
                    )

                    self.last_trigger_time = now

                    self.left_wink_start = None

            else:

                self.left_wink_start = None

            # =================================================
            # RIGHT WINK → FILE EXPLORER
            # =================================================

            if (
                RIGHT_CLOSED
                and not LEFT_CLOSED
            ):

                if self.right_wink_start is None:

                    self.right_wink_start = now

                elif (
                    now - self.right_wink_start
                    > 2
                ):

                    print(
                        "[EYE] RIGHT WINK → FILE EXPLORER"
                    )

                    subprocess.Popen(
                        "explorer"
                    )

                    self.last_trigger_time = now

                    self.right_wink_start = None

            else:

                self.right_wink_start = None

            # =================================================
            # BOTH EYES CLOSED → WHATSAPP
            # =================================================

            if (
                LEFT_CLOSED
                and RIGHT_CLOSED
            ):

                if self.both_eye_start is None:

                    self.both_eye_start = now

                elif (
                    now - self.both_eye_start
                    > 2
                ):

                    print(
                        "[EYE] BOTH EYES → WHATSAPP"
                    )

                    try:

                        subprocess.Popen(
                            [
                                "cmd",
                                "/c",
                                "start",
                                "whatsapp:"
                            ],
                            shell=True
                        )

                    except Exception as e:

                        print(
                            "[ERROR] WhatsApp launch failed:",
                            e
                        )

                    self.last_trigger_time = now

                    self.both_eye_start = None

            else:

                self.both_eye_start = None

        return avg_ear

    def get_cached_ear(
        self
    ) -> Optional[float]:

        return self._last_ear

    @staticmethod
    def _compute_ear(
        landmarks: list,
        eye_indices: list
    ) -> float:

        p1 = np.array(
            landmarks[eye_indices[0]]
        )

        p2 = np.array(
            landmarks[eye_indices[1]]
        )

        p3 = np.array(
            landmarks[eye_indices[2]]
        )

        p4 = np.array(
            landmarks[eye_indices[3]]
        )

        p5 = np.array(
            landmarks[eye_indices[4]]
        )

        p6 = np.array(
            landmarks[eye_indices[5]]
        )

        vertical_1 = np.linalg.norm(
            p2 - p6
        )

        vertical_2 = np.linalg.norm(
            p3 - p5
        )

        horizontal = np.linalg.norm(
            p1 - p4
        )

        if horizontal == 0:

            return 0.0

        ear = (
            vertical_1 + vertical_2
        ) / (
            2.0 * horizontal
        )

        return ear

    def release(self) -> None:

        self.face_mesh.close()
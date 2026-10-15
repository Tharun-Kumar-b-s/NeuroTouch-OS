# """
# NeuroTouch OS — Configuration Module
# =====================================
# All tunable constants, thresholds, and settings in one place.
# Adjust these values to fine-tune system behavior.
# """

# import ctypes

# # ---------------------------------------------------------------------------
# # Screen Resolution (auto-detected via Windows API)
# # ---------------------------------------------------------------------------
# SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
# SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)

# # ---------------------------------------------------------------------------
# # Camera Settings
# # ---------------------------------------------------------------------------
# CAMERA_INDEX = 0                 # Default webcam
# CAMERA_WIDTH = 640               # Capture width
# CAMERA_HEIGHT = 480              # Capture height
# CAMERA_FPS = 30                  # Requested FPS from webcam

# # ---------------------------------------------------------------------------
# # Cursor Smoothing Engine
# # ---------------------------------------------------------------------------
# CURSOR_SMOOTHING = 5

# # Smaller margins = easier corner reach
# CURSOR_FRAME_MARGIN_X = 15
# CURSOR_FRAME_MARGIN_Y = 15

# # ---------------------------------------------------------------------------
# # MediaPipe Hand Tracking
# # ---------------------------------------------------------------------------
# HAND_MAX_NUM_HANDS = 2
# HAND_MODEL_COMPLEXITY = 0        # 0 = fastest, 1 = more accurate
# HAND_MIN_DETECTION_CONF = 0.7
# HAND_MIN_TRACKING_CONF = 0.6

# # ---------------------------------------------------------------------------
# # MediaPipe Face Mesh
# # ---------------------------------------------------------------------------
# FACE_MAX_NUM_FACES = 1
# FACE_REFINE_LANDMARKS = True
# FACE_MIN_DETECTION_CONF = 0.6
# FACE_MIN_TRACKING_CONF = 0.5
# FACE_PROCESS_INTERVAL = 3        # Process face every N frames (saves CPU)

# # ---------------------------------------------------------------------------
# # Gesture Thresholds
# # ---------------------------------------------------------------------------
# # Finger-up detection: a finger is "up" if its tip is above its PIP joint
# # Thumb uses X-axis comparison instead of Y-axis
# PINCH_DISTANCE_THRESHOLD = 40    # Max pixel distance for pinch detection
# PALM_OPEN_MIN_FINGERS = 4        # Minimum fingers up to count as open palm

# # ---------------------------------------------------------------------------
# # Gesture Cooldowns (seconds) — prevents repeated triggers
# # ---------------------------------------------------------------------------
# COOLDOWN_LEFT_CLICK = 0.5
# COOLDOWN_RIGHT_CLICK = 0.6
# COOLDOWN_DOUBLE_CLICK = 0.7
# COOLDOWN_HOVER_TOGGLE = 1.5          # Debounce: prevents re-toggle within 1.5s
# COOLDOWN_VOICE_COMMAND = 0.8
# COOLDOWN_SCROLL = 0.05           # Per-scroll-step cooldown

# # ---------------------------------------------------------------------------
# # Voice Recognition
# # ---------------------------------------------------------------------------
# VOICE_ENERGY_THRESHOLD = 300     # Ambient noise energy threshold
# VOICE_PAUSE_THRESHOLD = 0.5     # Seconds of silence to end phrase
# VOICE_PHRASE_TIME_LIMIT = 3      # Max seconds for a single phrase
# VOICE_LISTEN_TIMEOUT = 2         # Timeout waiting for phrase start

# # ---------------------------------------------------------------------------
# # Drowsiness Detection
# # ---------------------------------------------------------------------------
# EAR_THRESHOLD = 0.21             # Eye Aspect Ratio below this = eyes closed
# DROWSINESS_ALARM_DELAY = 5.0    # Seconds of continuous closure before alarm
# DROWSINESS_BEEP_FREQ = 2500      # Alarm beep frequency (Hz)
# DROWSINESS_BEEP_DURATION = 300   # Alarm beep duration (ms)

# # ---------------------------------------------------------------------------
# # Scrolling
# # ---------------------------------------------------------------------------
# SCROLL_SPEED = 3                 # Scroll amount per tick
# SCROLL_INTERVAL = 0.05           # Seconds between scroll ticks

# # ---------------------------------------------------------------------------
# # Overlay / HUD
# # ---------------------------------------------------------------------------
# HUD_FONT_SCALE = 0.55
# HUD_THICKNESS = 1
# HUD_COLOR_GREEN = (0, 255, 100)
# HUD_COLOR_RED = (0, 0, 255)
# HUD_COLOR_YELLOW = (0, 220, 255)
# HUD_COLOR_CYAN = (255, 200, 0)
# HUD_COLOR_WHITE = (255, 255, 255)
# HUD_BG_COLOR = (30, 30, 30)
# HUD_BG_ALPHA = 0.6

# # ---------------------------------------------------------------------------
# # MediaPipe Landmark Indices (Hands)
# # ---------------------------------------------------------------------------
# # Fingertip landmarks
# INDEX_FINGER_TIP = 8
# INDEX_FINGER_PIP = 6
# MIDDLE_FINGER_TIP = 12
# MIDDLE_FINGER_PIP = 10
# RING_FINGER_TIP = 16
# RING_FINGER_PIP = 14
# PINKY_FINGER_TIP = 20
# PINKY_FINGER_PIP = 18
# THUMB_TIP = 4
# THUMB_IP = 3
# THUMB_MCP = 2
# WRIST = 0

# # ---------------------------------------------------------------------------
# # MediaPipe Landmark Indices (Face — Eyes)
# # ---------------------------------------------------------------------------
# # Right eye (user's right, appears as left in mirrored feed)
# RIGHT_EYE = [33, 160, 158, 133, 153, 144]
# # Left eye (user's left, appears as right in mirrored feed)
# LEFT_EYE = [362, 385, 387, 263, 373, 380]



"""
NeuroTouch OS — Configuration Module
=====================================
"""

import ctypes

# ---------------------------------------------------------------------------
# Screen Resolution
# ---------------------------------------------------------------------------

SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)

# ---------------------------------------------------------------------------
# Camera Settings
# ---------------------------------------------------------------------------

CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# ---------------------------------------------------------------------------
# CURSOR ENGINE
# ---------------------------------------------------------------------------

CURSOR_SMOOTHING = 7

CURSOR_FRAME_MARGIN_X = 100
CURSOR_FRAME_MARGIN_Y = 100

CURSOR_EDGE_ACCELERATION = 1.10

# ---------------------------------------------------------------------------
# MediaPipe Hand Tracking
# ---------------------------------------------------------------------------

HAND_MAX_NUM_HANDS = 2
HAND_MODEL_COMPLEXITY = 0

HAND_MIN_DETECTION_CONF = 0.72
HAND_MIN_TRACKING_CONF = 0.72

# ---------------------------------------------------------------------------
# Face Mesh
# ---------------------------------------------------------------------------

FACE_MAX_NUM_FACES = 1
FACE_REFINE_LANDMARKS = True
FACE_MIN_DETECTION_CONF = 0.6
FACE_MIN_TRACKING_CONF = 0.5
FACE_PROCESS_INTERVAL = 3

# ---------------------------------------------------------------------------
# Gesture Thresholds
# ---------------------------------------------------------------------------

PINCH_DISTANCE_THRESHOLD = 40
PALM_OPEN_MIN_FINGERS = 4

# ---------------------------------------------------------------------------
# Cooldowns
# ---------------------------------------------------------------------------

COOLDOWN_LEFT_CLICK = 0.5
COOLDOWN_RIGHT_CLICK = 0.6
COOLDOWN_DOUBLE_CLICK = 0.7
COOLDOWN_HOVER_TOGGLE = 1.2
COOLDOWN_VOICE_COMMAND = 0.8
COOLDOWN_SCROLL = 0.05

# ---------------------------------------------------------------------------
# Voice Recognition
# ---------------------------------------------------------------------------

VOICE_ENERGY_THRESHOLD = 120

VOICE_PAUSE_THRESHOLD = 0.8
VOICE_NON_SPEAKING_DURATION = 0.5

VOICE_PHRASE_TIME_LIMIT = 4
VOICE_LISTEN_TIMEOUT = 2

# ---------------------------------------------------------------------------
# Drowsiness Detection
# ---------------------------------------------------------------------------

EAR_THRESHOLD = 0.21

DROWSINESS_ALARM_DELAY = 5.0

DROWSINESS_BEEP_FREQ = 2500
DROWSINESS_BEEP_DURATION = 300

# ---------------------------------------------------------------------------
# Scrolling
# ---------------------------------------------------------------------------

SCROLL_SPEED = 3
SCROLL_INTERVAL = 0.05

# ---------------------------------------------------------------------------
# Overlay / HUD
# ---------------------------------------------------------------------------

HUD_FONT_SCALE = 0.55
HUD_THICKNESS = 1

HUD_COLOR_GREEN = (0, 255, 100)
HUD_COLOR_RED = (0, 0, 255)
HUD_COLOR_YELLOW = (0, 220, 255)
HUD_COLOR_CYAN = (255, 200, 0)
HUD_COLOR_WHITE = (255, 255, 255)

HUD_BG_COLOR = (30, 30, 30)
HUD_BG_ALPHA = 0.6

# ---------------------------------------------------------------------------
# MediaPipe Landmark Indices (Hands)
# ---------------------------------------------------------------------------

INDEX_FINGER_TIP = 8
INDEX_FINGER_PIP = 6

MIDDLE_FINGER_TIP = 12
MIDDLE_FINGER_PIP = 10

RING_FINGER_TIP = 16
RING_FINGER_PIP = 14

PINKY_FINGER_TIP = 20
PINKY_FINGER_PIP = 18

THUMB_TIP = 4
THUMB_IP = 3
THUMB_MCP = 2

WRIST = 0

# ---------------------------------------------------------------------------
# MediaPipe Landmark Indices (Face)
# ---------------------------------------------------------------------------

RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]


"""
NeuroTouch OS — HUD Overlay
==============================
Renders clean, minimal status information on the OpenCV display.
Dark-themed with semi-transparent backgrounds for readability.
"""

import cv2
import numpy as np
import time
import config as cfg


class Overlay:
    """
    Renders a futuristic HUD overlay on the webcam feed.
    
    Displays: FPS, hover status, gesture label, voice status,
    scroll status, drowsiness warning, and EAR value.
    """

    def __init__(self):
        self._fps_history = []
        self._last_time = time.time()
        self._frame_count = 0
        self._fps = 0.0

    def update_fps(self) -> float:
        """Calculate and return current FPS."""
        self._frame_count += 1
        now = time.time()
        elapsed = now - self._last_time
        if elapsed >= 0.5:  # Update FPS every 0.5 seconds
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._last_time = now
        return self._fps

    def render(self, frame: np.ndarray,
               hover_active: bool = False,
               gesture_label: str = "None",
               voice_status: str = "Listening...",
               voice_last_cmd: str = "",
               scroll_status: str = "None",
               drowsiness_warning: bool = False,
               ear_value: float = 0.0,
               keyboard_open: bool = False) -> np.ndarray:
        """
        Render the HUD overlay onto the frame.
        
        Args:
            frame: OpenCV BGR frame to draw on
            hover_active: Whether hover mode is ON
            gesture_label: Current detected gesture name
            voice_status: Voice engine status string
            voice_last_cmd: Last voice command heard
            scroll_status: Current scroll direction
            drowsiness_warning: Whether to show drowsiness alert
            ear_value: Current Eye Aspect Ratio
            keyboard_open: Whether on-screen keyboard is open
            
        Returns:
            Frame with overlay drawn
        """
        h, w = frame.shape[:2]
        fps = self.update_fps()

        # --- Top-left panel: System Status ---
        panel_lines = [
            f"FPS: {fps:.0f}",
            f"Hover: {'ON' if hover_active else 'OFF'}",
            f"Gesture: {gesture_label}",
            f"Scroll: {scroll_status}",
            f"Keyboard: {'OPEN' if keyboard_open else 'closed'}",
        ]
        self._draw_panel(frame, 10, 10, panel_lines, hover_active)

        # --- Top-right panel: Voice Status ---
        voice_lines = [
            f"Voice: {voice_status}",
        ]
        if voice_last_cmd:
            voice_lines.append(f'Last: "{voice_last_cmd}"')
        self._draw_panel_right(frame, w - 10, 10, voice_lines)

        # --- Bottom-left: EAR & Eye Status ---
        if ear_value > 0:
            ear_color = cfg.HUD_COLOR_GREEN if ear_value > cfg.EAR_THRESHOLD else cfg.HUD_COLOR_RED
            eye_status = "OPEN" if ear_value > cfg.EAR_THRESHOLD else "CLOSED"
            ear_lines = [
                f"EAR: {ear_value:.2f} | Eyes: {eye_status}",
            ]
            self._draw_panel(frame, 10, h - 45, ear_lines, False, ear_color)

        # --- Drowsiness Warning (center, flashing) ---
        if drowsiness_warning:
            self._draw_drowsiness_warning(frame, w, h)

        # --- Title bar ---
        cv2.putText(frame, "NeuroTouch OS", (w // 2 - 80, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, cfg.HUD_COLOR_CYAN, 1,
                    cv2.LINE_AA)

        return frame

    def _draw_panel(self, frame, x, y, lines, highlight=False, color=None):
        """Draw a semi-transparent panel with text lines."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = cfg.HUD_FONT_SCALE
        thick = cfg.HUD_THICKNESS
        line_h = 22
        padding = 8

        # Calculate panel size
        max_w = 0
        for line in lines:
            (tw, _), _ = cv2.getTextSize(line, font, scale, thick)
            max_w = max(max_w, tw)

        panel_w = max_w + padding * 2
        panel_h = len(lines) * line_h + padding * 2

        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + panel_w, y + panel_h),
                      cfg.HUD_BG_COLOR, -1)
        cv2.addWeighted(overlay, cfg.HUD_BG_ALPHA, frame,
                        1 - cfg.HUD_BG_ALPHA, 0, frame)

        # Draw border
        border_color = cfg.HUD_COLOR_CYAN if highlight else (80, 80, 80)
        cv2.rectangle(frame, (x, y), (x + panel_w, y + panel_h),
                      border_color, 1)

        # Draw text
        for i, line in enumerate(lines):
            text_color = color if color else cfg.HUD_COLOR_GREEN
            if "OFF" in line:
                text_color = (100, 100, 100)
            elif "ON" in line or "OPEN" in line.upper():
                text_color = cfg.HUD_COLOR_GREEN
            cv2.putText(frame, line,
                        (x + padding, y + padding + (i + 1) * line_h - 4),
                        font, scale, text_color, thick, cv2.LINE_AA)

    def _draw_panel_right(self, frame, right_x, y, lines):
        """Draw a right-aligned panel."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = cfg.HUD_FONT_SCALE
        thick = cfg.HUD_THICKNESS
        line_h = 22
        padding = 8

        max_w = 0
        for line in lines:
            (tw, _), _ = cv2.getTextSize(line, font, scale, thick)
            max_w = max(max_w, tw)

        panel_w = max_w + padding * 2
        panel_h = len(lines) * line_h + padding * 2
        x = right_x - panel_w

        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + panel_w, y + panel_h),
                      cfg.HUD_BG_COLOR, -1)
        cv2.addWeighted(overlay, cfg.HUD_BG_ALPHA, frame,
                        1 - cfg.HUD_BG_ALPHA, 0, frame)
        cv2.rectangle(frame, (x, y), (x + panel_w, y + panel_h),
                      (80, 80, 80), 1)

        for i, line in enumerate(lines):
            cv2.putText(frame, line,
                        (x + padding, y + padding + (i + 1) * line_h - 4),
                        font, scale, cfg.HUD_COLOR_YELLOW, thick, cv2.LINE_AA)

    def _draw_drowsiness_warning(self, frame, w, h):
        """Draw flashing drowsiness warning in center of screen."""
        # Flash effect using time
        if int(time.time() * 3) % 2 == 0:
            # Red overlay flash
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 80), -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # Warning text
        text = "!! DROWSINESS ALERT !!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1.2
        thick = 3
        (tw, th), _ = cv2.getTextSize(text, font, scale, thick)
        tx = (w - tw) // 2
        ty = h // 2

        # Black outline for readability
        cv2.putText(frame, text, (tx, ty), font, scale, (0, 0, 0), thick + 2, cv2.LINE_AA)
        # Red text
        cv2.putText(frame, text, (tx, ty), font, scale, (0, 0, 255), thick, cv2.LINE_AA)

        sub_text = "WAKE UP! Open your eyes!"
        (sw, _), _ = cv2.getTextSize(sub_text, font, 0.7, 2)
        cv2.putText(frame, sub_text, ((w - sw) // 2, ty + 40),
                    font, 0.7, (0, 0, 255), 2, cv2.LINE_AA)



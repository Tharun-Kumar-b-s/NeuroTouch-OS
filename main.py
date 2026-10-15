# """
# NeuroTouch OS — Main Orchestrator
# ===================================
# Entry point for the touchless OS controller.
# """

# import cv2
# import sys
# import numpy as np
# import pyautogui
# from modules.ai_voice import AIVoice
# from modules.sound_engine import SoundEngine

# # Import all modules
# import config as cfg
# from modules.hand_tracker import HandTracker
# from modules.face_detector import FaceDetector
# from modules.gesture_engine import GestureEngine, GestureType
# from modules.cursor_engine import CursorEngine
# from modules.voice_engine import VoiceEngine
# from modules.os_automation import OSAutomation
# from modules.drowsiness import DrowsinessDetector
# from modules.keyboard_manager import KeyboardManager
# from modules.event_manager import EventManager
# from modules.overlay import Overlay


# pyautogui.FAILSAFE = False
# pyautogui.PAUSE = 0


# def main():

#     print("=" * 55)
#     print("  NeuroTouch OS — Touchless Operating System Controller")
#     print("=" * 55)

#     print()
#     print(f"  Screen: {cfg.SCREEN_WIDTH} x {cfg.SCREEN_HEIGHT}")
#     print(f"  Camera: {cfg.CAMERA_WIDTH} x {cfg.CAMERA_HEIGHT}")

#     print()
#     print("  Starting modules...")

#     # ============================================================
#     # MODULES
#     # ============================================================

#     hand_tracker = HandTracker()
#     face_detector = FaceDetector()
#     gesture_engine = GestureEngine()
#     cursor_engine = CursorEngine()

#     voice_engine = VoiceEngine()
#     os_auto = OSAutomation()
#     drowsiness = DrowsinessDetector()
#     keyboard_mgr = KeyboardManager()
#     event_mgr = EventManager()
#     overlay = Overlay()

#     print("  [OK] All modules initialized")

#     # ============================================================
#     # CAMERA
#     # ============================================================

#     cap = cv2.VideoCapture(
#         cfg.CAMERA_INDEX,
#         cv2.CAP_DSHOW
#     )

#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.CAMERA_WIDTH)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.CAMERA_HEIGHT)

#     cap.set(cv2.CAP_PROP_FPS, cfg.CAMERA_FPS)

#     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

#     cap.set(
#         cv2.CAP_PROP_FOURCC,
#         cv2.VideoWriter_fourcc(*'MJPG')
#     )

#     cap.set(cv2.CAP_PROP_BRIGHTNESS, 140)
#     cap.set(cv2.CAP_PROP_CONTRAST, 45)

#     if not cap.isOpened():

#         print("  [ERROR] Cannot open webcam.")

#         sys.exit(1)

#     print("  [OK] Webcam initialized")

#     # ============================================================
#     # VOICE
#     # ============================================================

#     voice_engine.start()

#     print("  [OK] Voice engine started")

#     print()
#     print("  System READY. Press ESC to quit.")
#     print("  Open palm → Toggle hover mode")
#     print("  Index finger → Move cursor")
#     print("-" * 55)

#     # ============================================================
#     # STATE VARIABLES
#     # ============================================================

#     frame_count = 0
#     current_gesture_label = "None"
#     current_ear = 0.0

#     # ============================================================
#     # MAIN LOOP
#     # ============================================================

#     try:

#         while True:

#             # ----------------------------------------------------
#             # FRAME
#             # ----------------------------------------------------

#             ret, frame = cap.read()

#             if not ret:

#                 print("[WARN] Frame capture failed")

#                 continue

#             frame_count += 1

#             frame = cv2.flip(frame, 1)

#             frame_h, frame_w = frame.shape[:2]

#             frame_rgb = cv2.cvtColor(
#                 frame,
#                 cv2.COLOR_BGR2RGB
#             )

#             # ----------------------------------------------------
#             # HAND TRACKING
#             # ----------------------------------------------------

#             hands = hand_tracker.process(
#                 frame_rgb,
#                 frame_w,
#                 frame_h
#             )

#             for hand in hands:

#                 hand_tracker.draw_landmarks(
#                     frame,
#                     hand
#                 )

#             # ====================================================
#             # CURSOR MOVEMENT
#             # ====================================================

#             if (
#                 gesture_engine.hover_active
#                 and len(hands) > 0
#             ):

#                 hand = hands[0]

#                 index_tip = hand.landmark_pixels[
#                     cfg.INDEX_FINGER_TIP
#                 ]

#                 x, y = index_tip

#                 screen_x = np.interp(
#                     x,
#                     (
#                         cfg.CURSOR_FRAME_MARGIN_X,
#                         frame_w - cfg.CURSOR_FRAME_MARGIN_X
#                     ),
#                     (
#                         0,
#                         cfg.SCREEN_WIDTH
#                     )
#                 )

#                 screen_y = np.interp(
#                     y,
#                     (
#                         cfg.CURSOR_FRAME_MARGIN_Y,
#                         frame_h - cfg.CURSOR_FRAME_MARGIN_Y
#                     ),
#                     (
#                         0,
#                         cfg.SCREEN_HEIGHT
#                     )
#                 )

#                 curr_x = cursor_engine._prev_x + (
#                     screen_x - cursor_engine._prev_x
#                 ) / cfg.CURSOR_SMOOTHING

#                 curr_y = cursor_engine._prev_y + (
#                     screen_y - cursor_engine._prev_y
#                 ) / cfg.CURSOR_SMOOTHING

#                 cursor_engine._prev_x = curr_x
#                 cursor_engine._prev_y = curr_y

#                 pyautogui.moveTo(
#                     curr_x,
#                     curr_y
#                 )

#             # ----------------------------------------------------
#             # FACE
#             # ----------------------------------------------------

#             if frame_count % cfg.FACE_PROCESS_INTERVAL == 0:

#                 ear_value = face_detector.process(
#                     frame_rgb,
#                     frame_w,
#                     frame_h
#                 )

#             else:

#                 ear_value = face_detector.get_cached_ear()

#             if ear_value is not None:

#                 current_ear = ear_value

#             # ----------------------------------------------------
#             # GESTURES
#             # ----------------------------------------------------

#             gestures = gesture_engine.classify(
#                 hands,
#                 frame_w,
#                 frame_h
#             )

#             current_gesture_label = "None"

#             for gesture_result in gestures:

#                 gt = gesture_result.gesture

                

#                 # ------------------------------------------------
#                 # HOVER ON
#                 # ------------------------------------------------

#                 if gt == GestureType.HOVER_ON:

#                     current_gesture_label = "Hover ON"

#                     print("[GESTURE] Hover Mode ON")

#                 # ------------------------------------------------
#                 # HOVER OFF
#                 # ------------------------------------------------

#                 elif gt == GestureType.HOVER_OFF:

#                     current_gesture_label = "Hover OFF"

#                     print("[GESTURE] Hover Mode OFF")

#             # ----------------------------------------------------
#             # VOICE
#             # ----------------------------------------------------

#             voice_cmd = voice_engine.poll_command()

#             if (
#                 voice_cmd
#                 and event_mgr.try_trigger(
#                     "voice_command"
#                 )
#             ):

#                 _execute_voice_command(
#                     voice_cmd,
#                     os_auto,
#                     keyboard_mgr,
#                     event_mgr
#                 )

#             # ----------------------------------------------------
#             # SCROLL
#             # ----------------------------------------------------

#             os_auto.update_scroll()

#             # ----------------------------------------------------
#             # DROWSINESS
#             # ----------------------------------------------------

#             drowsy_alert = drowsiness.update(
#                 ear_value
#             )

#             # ----------------------------------------------------
#             # OVERLAY
#             # ----------------------------------------------------

#             frame = overlay.render(
#                 frame,
#                 hover_active=gesture_engine.hover_active,
#                 gesture_label=current_gesture_label,
#                 voice_status=voice_engine.status,
#                 voice_last_cmd=voice_engine.last_text,
#                 scroll_status=os_auto.scroll_direction_label,
#                 drowsiness_warning=drowsy_alert,
#                 ear_value=current_ear,
#                 keyboard_open=keyboard_mgr.is_open,
#             )

#             # ----------------------------------------------------
#             # DISPLAY
#             # ----------------------------------------------------

#             cv2.imshow(
#                 "NeuroTouch OS",
#                 frame
#             )

#             if cv2.waitKey(1) & 0xFF == 27:

#                 print("\n[INFO] ESC pressed")

#                 break

#     except KeyboardInterrupt:

#         print("\n[INFO] Keyboard interrupt")

#     finally:

#         print("[INFO] Releasing resources...")

#         voice_engine.stop()

#         hand_tracker.release()
#         face_detector.release()
#         drowsiness.release()
#         keyboard_mgr.release()

#         cap.release()

#         cv2.destroyAllWindows()

#         print("[INFO] NeuroTouch OS stopped")


# # ================================================================
# # VOICE COMMANDS
# # ================================================================

# def _execute_voice_command(
#     cmd: str,
#     os_auto: OSAutomation,
#     keyboard_mgr: KeyboardManager,
#     event_mgr: EventManager
# ) -> None:

#     # ============================================================
#     # LEFT CLICK
#     # ============================================================

#     if cmd == "left_click":

#         os_auto.left_click()

#         print("[VOICE] Left Click")

#     # ============================================================
#     # RIGHT CLICK
#     # ============================================================

#     elif cmd == "right_click":

#         os_auto.right_click()

#         print("[VOICE] Right Click")

#     # ============================================================
#     # DOUBLE CLICK
#     # ============================================================

#     elif cmd == "double_click":

#         os_auto.double_click()

#         print("[VOICE] Double Click")

#     # ============================================================
#     # SCROLL UP
#     # ============================================================

#     elif cmd == "scroll_up":

#         os_auto.start_scroll("up")

#         print("[VOICE] Scroll Up")

#     # ============================================================
#     # SCROLL DOWN
#     # ============================================================

#     elif cmd == "scroll_down":

#         os_auto.start_scroll("down")

#         print("[VOICE] Scroll Down")

#     # ============================================================
#     # STOP SCROLL
#     # ============================================================

#     elif cmd == "stop_scroll":

#         os_auto.stop_scroll()

#         print("[VOICE] Scroll Stopped")

#     # ============================================================
#     # OPEN KEYBOARD
#     # ============================================================

#     elif cmd == "keyboard_open":

#         if event_mgr.try_trigger(
#             "keyboard_open"
#         ):

#             keyboard_mgr.open_keyboard()

#             print("[VOICE] Keyboard Opened")

#     # ============================================================
#     # CLOSE KEYBOARD
#     # ============================================================

#     elif cmd == "keyboard_close":

#         if event_mgr.try_trigger(
#             "keyboard_close"
#         ):

#             keyboard_mgr.close_keyboard()

#             print("[VOICE] Keyboard Closed")


# # ================================================================
# # ENTRY
# # ================================================================

# if __name__ == "__main__":
#     main()

"""
NeuroTouch OS — Main Orchestrator
===================================
Entry point for the touchless OS controller.
"""

import cv2
import sys
import time
import subprocess
import numpy as np
import pyautogui

from modules.ai_voice import AIVoice
from modules.sound_engine import SoundEngine

# Import all modules
import config as cfg
from modules.hand_tracker import HandTracker
from modules.face_detector import FaceDetector
from modules.gesture_engine import GestureEngine, GestureType
from modules.cursor_engine import CursorEngine
from modules.voice_engine import VoiceEngine
from modules.os_automation import OSAutomation
from modules.drowsiness import DrowsinessDetector
from modules.keyboard_manager import KeyboardManager
from modules.event_manager import EventManager
from modules.overlay import Overlay


pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


def main():

    print("=" * 55)
    print("  NeuroTouch OS — Touchless Operating System Controller")
    print("=" * 55)

    print()
    print(f"  Screen: {cfg.SCREEN_WIDTH} x {cfg.SCREEN_HEIGHT}")
    print(f"  Camera: {cfg.CAMERA_WIDTH} x {cfg.CAMERA_HEIGHT}")

    print()
    print("  Starting modules...")

    # ============================================================
    # MODULES
    # ============================================================

    hand_tracker = HandTracker()
    face_detector = FaceDetector()
    gesture_engine = GestureEngine()
    cursor_engine = CursorEngine()

    voice_engine = VoiceEngine()
    os_auto = OSAutomation()
    drowsiness = DrowsinessDetector()
    keyboard_mgr = KeyboardManager()
    event_mgr = EventManager()
    overlay = Overlay()

    ai_voice = AIVoice()
    sound_engine = SoundEngine()

    print("  [OK] All modules initialized")

    # ============================================================
    # CAMERA
    # ============================================================

    cap = cv2.VideoCapture(
        cfg.CAMERA_INDEX,
        cv2.CAP_DSHOW
    )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.CAMERA_HEIGHT)

    cap.set(cv2.CAP_PROP_FPS, cfg.CAMERA_FPS)

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    cap.set(
        cv2.CAP_PROP_FOURCC,
        cv2.VideoWriter_fourcc(*'MJPG')
    )

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 140)
    cap.set(cv2.CAP_PROP_CONTRAST, 45)

    if not cap.isOpened():

        print("  [ERROR] Cannot open webcam.")

        sys.exit(1)

    print("  [OK] Webcam initialized")

    # ============================================================
    # VOICE
    # ============================================================

    voice_engine.start()

    print("  [OK] Voice engine started")

    sound_engine.play(
        "assets/sounds/startup.wav"
    )

    ai_voice.speak(
        "NeuroTouch Operating System initialized"
    )

    print()
    print("  System READY. Press ESC to quit.")
    print("  Open palm → Toggle hover mode")
    print("  Index finger → Move cursor")
    print("-" * 55)

    # ============================================================
    # STATE VARIABLES
    # ============================================================

    frame_count = 0
    current_gesture_label = "None"
    current_ear = 0.0

    last_air_button_time = 0

    # ============================================================
    # MAIN LOOP
    # ============================================================

    try:

        while True:

            # ----------------------------------------------------
            # FRAME
            # ----------------------------------------------------

            ret, frame = cap.read()

            if not ret:

                print("[WARN] Frame capture failed")

                continue

            frame_count += 1

            frame = cv2.flip(frame, 1)

            frame_h, frame_w = frame.shape[:2]

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # ----------------------------------------------------
            # HAND TRACKING
            # ----------------------------------------------------

            hands = hand_tracker.process(
                frame_rgb,
                frame_w,
                frame_h
            )

            for hand in hands:

                hand_tracker.draw_landmarks(
                    frame,
                    hand
                )

            # ====================================================
            # CURSOR MOVEMENT
            # ====================================================

            if (
                gesture_engine.hover_active
                and len(hands) > 0
            ):

                hand = hands[0]

                index_tip = hand.landmark_pixels[
                    cfg.INDEX_FINGER_TIP
                ]

                x, y = index_tip

                screen_x = np.interp(
                    x,
                    (
                        cfg.CURSOR_FRAME_MARGIN_X,
                        frame_w - cfg.CURSOR_FRAME_MARGIN_X
                    ),
                    (
                        0,
                        cfg.SCREEN_WIDTH
                    )
                )

                screen_y = np.interp(
                    y,
                    (
                        cfg.CURSOR_FRAME_MARGIN_Y,
                        frame_h - cfg.CURSOR_FRAME_MARGIN_Y
                    ),
                    (
                        0,
                        cfg.SCREEN_HEIGHT
                    )
                )

                curr_x = cursor_engine._prev_x + (
                    screen_x - cursor_engine._prev_x
                ) / cfg.CURSOR_SMOOTHING

                curr_y = cursor_engine._prev_y + (
                    screen_y - cursor_engine._prev_y
                ) / cfg.CURSOR_SMOOTHING

                cursor_engine._prev_x = curr_x
                cursor_engine._prev_y = curr_y

                pyautogui.moveTo(
                    curr_x,
                    curr_y
                )

            # ----------------------------------------------------
            # FACE
            # ----------------------------------------------------

            if frame_count % cfg.FACE_PROCESS_INTERVAL == 0:

                ear_value = face_detector.process(
                    frame_rgb,
                    frame_w,
                    frame_h
                )

            else:

                ear_value = face_detector.get_cached_ear()

            if ear_value is not None:

                current_ear = ear_value

            # ----------------------------------------------------
            # GESTURES
            # ----------------------------------------------------

            gestures = gesture_engine.classify(
                hands,
                frame_w,
                frame_h
            )

            current_gesture_label = "None"

            for gesture_result in gestures:

                gt = gesture_result.gesture

                # ------------------------------------------------
                # HOVER ON
                # ------------------------------------------------

                if gt == GestureType.HOVER_ON:

                    current_gesture_label = "Hover ON"

                    print("[GESTURE] Hover Mode ON")

                    ai_voice.speak(
                        "Hover mode activated"
                    )

                    sound_engine.play(
                        "assets/sounds/hover_on.wav"
                    )

                # ------------------------------------------------
                # HOVER OFF
                # ------------------------------------------------

                elif gt == GestureType.HOVER_OFF:

                    current_gesture_label = "Hover OFF"

                    print("[GESTURE] Hover Mode OFF")

                    ai_voice.speak(
                        "Hover mode disabled"
                    )

                    sound_engine.play(
                        "assets/sounds/hover_off.wav"
                    )

            # ----------------------------------------------------
            # VOICE
            # ----------------------------------------------------

            voice_cmd = voice_engine.poll_command()

            if (
                voice_cmd
                and event_mgr.try_trigger(
                    "voice_command"
                )
            ):

                _execute_voice_command(
                    voice_cmd,
                    os_auto,
                    keyboard_mgr,
                    event_mgr,
                    ai_voice,
                    sound_engine
                )

            # ----------------------------------------------------
            # SCROLL
            # ----------------------------------------------------

            os_auto.update_scroll()

            # ----------------------------------------------------
            # DROWSINESS
            # ----------------------------------------------------

            drowsy_alert = drowsiness.update(
                ear_value
            )

            # ----------------------------------------------------
            # OVERLAY
            # ----------------------------------------------------

            frame = overlay.render(
                frame,
                hover_active=gesture_engine.hover_active,
                gesture_label=current_gesture_label,
                voice_status=voice_engine.status,
                voice_last_cmd=voice_engine.last_text,
                scroll_status=os_auto.scroll_direction_label,
                drowsiness_warning=drowsy_alert,
                ear_value=current_ear,
                keyboard_open=keyboard_mgr.is_open,
            )

            # ====================================================
            # VIRTUAL AIR BUTTONS
            # ====================================================

            button_y = 50
            button_w = 170
            button_h = 60

            chrome_btn = (
                40,
                button_y,
                40 + button_w,
                button_y + button_h
            )

            whatsapp_btn = (
                240,
                button_y,
                240 + button_w,
                button_y + button_h
            )

            explorer_btn = (
                440,
                button_y,
                440 + button_w,
                button_y + button_h
            )

            # DRAW BUTTONS

            cv2.rectangle(
                frame,
                (chrome_btn[0], chrome_btn[1]),
                (chrome_btn[2], chrome_btn[3]),
                (255, 255, 0),
                -1
            )

            cv2.rectangle(
                frame,
                (whatsapp_btn[0], whatsapp_btn[1]),
                (whatsapp_btn[2], whatsapp_btn[3]),
                (0, 255, 0),
                -1
            )

            cv2.rectangle(
                frame,
                (explorer_btn[0], explorer_btn[1]),
                (explorer_btn[2], explorer_btn[3]),
                (255, 100, 0),
                -1
            )

            cv2.putText(
                frame,
                "CHROME",
                (70, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2
            )

            cv2.putText(
                frame,
                "WHATSAPP",
                (255, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2
            )

            cv2.putText(
                frame,
                "EXPLORER",
                (460, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2
            )

            # AIR TOUCH DETECTION

            if len(hands) > 0:

                hand = hands[0]

                index_x, index_y = hand.landmark_pixels[
                    cfg.INDEX_FINGER_TIP
                ]

                cv2.circle(
                    frame,
                    (index_x, index_y),
                    15,
                    (0, 0, 255),
                    -1
                )

                now = time.time()

                if now - last_air_button_time > 2:

                    # CHROME

                    if (
                        chrome_btn[0] < index_x < chrome_btn[2]
                        and
                        chrome_btn[1] < index_y < chrome_btn[3]
                    ):

                        subprocess.Popen(
                            "start chrome",
                            shell=True
                        )

                        ai_voice.speak(
                            "Opening Chrome"
                        )

                        sound_engine.play(
                            "assets/sounds/click.wav"
                        )

                        last_air_button_time = now

                    # WHATSAPP

                    elif (
                        whatsapp_btn[0] < index_x < whatsapp_btn[2]
                        and
                        whatsapp_btn[1] < index_y < whatsapp_btn[3]
                    ):

                        subprocess.Popen(
                            "start whatsapp:",
                            shell=True
                        )

                        ai_voice.speak(
                            "Opening WhatsApp"
                        )

                        sound_engine.play(
                            "assets/sounds/click.wav"
                        )

                        last_air_button_time = now

                    # EXPLORER

                    elif (
                        explorer_btn[0] < index_x < explorer_btn[2]
                        and
                        explorer_btn[1] < index_y < explorer_btn[3]
                    ):

                        subprocess.Popen(
                            "explorer"
                        )

                        ai_voice.speak(
                            "Opening File Explorer"
                        )

                        sound_engine.play(
                            "assets/sounds/click.wav"
                        )

                        last_air_button_time = now

            # ----------------------------------------------------
            # DISPLAY
            # ----------------------------------------------------

            cv2.imshow(
                "NeuroTouch OS",
                frame
            )

            if cv2.waitKey(1) & 0xFF == 27:

                print("\n[INFO] ESC pressed")

                break

    except KeyboardInterrupt:

        print("\n[INFO] Keyboard interrupt")

    finally:

        print("[INFO] Releasing resources...")

        voice_engine.stop()

        hand_tracker.release()
        face_detector.release()
        drowsiness.release()
        keyboard_mgr.release()

        cap.release()

        cv2.destroyAllWindows()

        print("[INFO] NeuroTouch OS stopped")


# ================================================================
# VOICE COMMANDS
# ================================================================

def _execute_voice_command(
    cmd: str,
    os_auto: OSAutomation,
    keyboard_mgr: KeyboardManager,
    event_mgr: EventManager,
    ai_voice,
    sound_engine
) -> None:

    # ============================================================
    # LEFT CLICK
    # ============================================================

    if cmd == "left_click":

        os_auto.left_click()

        sound_engine.play(
            "assets/sounds/click.wav"
        )

        ai_voice.speak(
            "Left click executed"
        )

        print("[VOICE] Left Click")

    # ============================================================
    # RIGHT CLICK
    # ============================================================

    elif cmd == "right_click":

        os_auto.right_click()

        sound_engine.play(
            "assets/sounds/click.wav"
        )

        ai_voice.speak(
            "Right click executed"
        )

        print("[VOICE] Right Click")

    # ============================================================
    # DOUBLE CLICK
    # ============================================================

    elif cmd == "double_click":

        os_auto.double_click()

        sound_engine.play(
            "assets/sounds/click.wav"
        )

        ai_voice.speak(
            "Double click executed"
        )

        print("[VOICE] Double Click")

    # ============================================================
    # SCROLL UP
    # ============================================================

    elif cmd == "scroll_up":

        os_auto.start_scroll("up")

        ai_voice.speak(
            "Scrolling up"
        )

        print("[VOICE] Scroll Up")

    # ============================================================
    # SCROLL DOWN
    # ============================================================

    elif cmd == "scroll_down":

        os_auto.start_scroll("down")

        ai_voice.speak(
            "Scrolling down"
        )

        print("[VOICE] Scroll Down")

    # ============================================================
    # STOP SCROLL
    # ============================================================

    elif cmd == "stop_scroll":

        os_auto.stop_scroll()

        ai_voice.speak(
            "Scroll stopped"
        )

        print("[VOICE] Scroll Stopped")

    # ============================================================
    # OPEN KEYBOARD
    # ============================================================

    elif cmd == "keyboard_open":

        if event_mgr.try_trigger(
            "keyboard_open"
        ):

            keyboard_mgr.open_keyboard()

            ai_voice.speak(
                "Opening keyboard"
            )

            print("[VOICE] Keyboard Opened")

    # ============================================================
    # CLOSE KEYBOARD
    # ============================================================

    elif cmd == "keyboard_close":

        if event_mgr.try_trigger(
            "keyboard_close"
        ):

            keyboard_mgr.close_keyboard()

            ai_voice.speak(
                "Closing keyboard"
            )

            print("[VOICE] Keyboard Closed")


# ================================================================
# ENTRY
# ================================================================

if __name__ == "__main__":
    main()
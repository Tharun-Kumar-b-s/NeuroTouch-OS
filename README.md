# NeuroTouch OS

**AI-Powered Touchless Operating System Controller**

Control your Windows PC using hand gestures, voice commands, and eye-state detection — no mouse or keyboard needed.

---

## Features

- **Hand Gesture Control** — Move cursor, click, right-click, double-click using hand gestures
- **Voice Commands** — Click, scroll, open/close keyboard via voice
- **Drowsiness Detection** — Alarm after 60 seconds of continuous eye closure
- **On-Screen Keyboard** — Windows accessibility keyboard for text input
- **Ultra-Smooth Cursor** — Velocity-adaptive EMA smoothing with dead-zone filtering
- **Real-Time HUD** — FPS counter, gesture status, voice status overlay
- **Multithreaded** — Voice runs in background thread, never blocks cursor

---

## Installation

### Prerequisites
- Python 3.8+
- Windows 10/11
- Webcam
- Microphone

### Steps

```bash
# 1. Navigate to project directory
cd mousecontrolledproj

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

> **Note:** PyAudio may require special installation on Windows:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

---

## Usage

### Starting the System
```bash
python main.py
```
Press **ESC** to quit.

### Gesture Reference

| Gesture | Hand | Action |
|---------|------|--------|
| Open palm (4+ fingers) | Left | Enable hover/cursor mode |
| Close fist / remove hand | Left | Disable hover mode |
| Index finger movement | Right | Move system cursor |
| Index + thumb pinch | Right | Left click |
| Peace sign (index + middle) | Left | Right click |
| Thumbs up (thumb only) | Left | Double click |

### Voice Commands

| Command | Action |
|---------|--------|
| "click" | Left click |
| "double click" | Double click |
| "right click" | Right click |
| "scroll up" | Start scrolling up |
| "scroll down" | Start scrolling down |
| "stop" / "stop scroll" | Stop scrolling |
| "keyboard" | Open on-screen keyboard |
| "close keyboard" | Close on-screen keyboard |

### Workflow
1. Show your **left hand open palm** to activate hover mode
2. Move your **right hand index finger** to control the cursor
3. **Pinch** index + thumb on right hand to click
4. Use **voice commands** for scrolling and keyboard
5. Close left hand or remove it to deactivate hover mode

---

## Architecture

```
main.py                    ← Entry point / main loop
config.py                  ← All tunable constants
modules/
├── hand_tracker.py        ← MediaPipe Hands wrapper
├── face_detector.py       ← MediaPipe FaceMesh + EAR
├── gesture_engine.py      ← Gesture classification
├── cursor_engine.py       ← Smooth cursor (EMA + ctypes)
├── voice_engine.py        ← Threaded speech recognition
├── os_automation.py       ← PyAutoGUI clicks/scroll
├── drowsiness.py          ← Eye closure alarm
├── keyboard_manager.py    ← Windows OSK control
├── event_manager.py       ← Cooldown/debouncing
└── overlay.py             ← HUD rendering
```

---

## Performance Optimizations

- **No `time.sleep()`** in main loop — timestamp-based cooldowns only
- **Face mesh every 3rd frame** — eyes don't change that fast
- **MediaPipe `model_complexity=0`** — fastest inference
- **ctypes `SetCursorPos`** — direct Windows API (faster than PyAutoGUI)
- **Velocity-adaptive smoothing** — responsive at speed, stable at rest
- **Thread-safe voice queue** — non-blocking command polling
- **Camera buffer size = 1** — minimizes frame delay

---

## Configuration

Edit `config.py` to tune:
- Cursor smoothing (`CURSOR_SMOOTHING_ALPHA`)
- Sensitivity (`CURSOR_SENSITIVITY`)
- Gesture cooldowns (`COOLDOWN_*`)
- Drowsiness threshold (`DROWSINESS_ALARM_DELAY`)
- Voice settings (`VOICE_*`)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Webcam not detected | Check `CAMERA_INDEX` in config.py |
| Cursor jittery | Increase `CURSOR_SMOOTHING_ALPHA` |
| Cursor too slow | Decrease frame margins, increase sensitivity |
| Voice not working | Check microphone, ensure internet connection |
| PyAudio install fails | Use `pipwin install pyaudio` |
| OSK won't open | Run as administrator |

---

## License

MIT License — Free for personal and commercial use.

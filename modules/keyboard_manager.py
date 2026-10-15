"""
NeuroTouch OS — On-Screen Keyboard Manager
============================================
Controls the Windows On-Screen Keyboard (osk.exe).
Opens/closes via subprocess for global accessibility input.
"""

import subprocess
import os
from typing import Optional


class KeyboardManager:
    """Manages the Windows On-Screen Keyboard (osk.exe)."""

    def __init__(self):
        self._is_open = False
        self._process: Optional[subprocess.Popen] = None

    @property
    def is_open(self) -> bool:
        """Whether the on-screen keyboard is currently open."""
        return self._is_open

    def open_keyboard(self) -> bool:
        """
        Open the Windows On-Screen Keyboard.
        
        Returns:
            True if keyboard was opened, False if already open or error
        """
        if self._is_open:
            return False

        try:
            # Use the Windows on-screen keyboard
            # osk.exe requires running from system32 on some Windows versions
            osk_path = os.path.join(
                os.environ.get("WINDIR", "C:\\Windows"),
                "System32", "osk.exe"
            )
            
            if os.path.exists(osk_path):
                self._process = subprocess.Popen(
                    [osk_path],
                    shell=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Fallback: try running osk directly
                self._process = subprocess.Popen(
                    ["osk"],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            self._is_open = True
            return True

        except (OSError, FileNotFoundError, subprocess.SubprocessError) as e:
            print(f"[KeyboardManager] Failed to open keyboard: {e}")
            # Try TabTip (touch keyboard) as alternative
            try:
                tabtip = os.path.join(
                    os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                    "Common Files", "microsoft shared", "ink", "TabTip.exe"
                )
                if os.path.exists(tabtip):
                    subprocess.Popen([tabtip], shell=False)
                    self._is_open = True
                    return True
            except Exception:
                pass
            return False

    def close_keyboard(self) -> bool:
        """
        Close the Windows On-Screen Keyboard.
        
        Returns:
            True if keyboard was closed, False if not open or error
        """
        if not self._is_open:
            return False

        try:
            # Kill osk.exe process
            subprocess.run(
                ["taskkill", "/f", "/im", "osk.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
            )
        except Exception:
            pass

        try:
            # Also try killing TabTip
            subprocess.run(
                ["taskkill", "/f", "/im", "TabTip.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
            )
        except Exception:
            pass

        self._is_open = False
        return True

    def toggle(self) -> bool:
        """Toggle keyboard open/close. Returns new state."""
        if self._is_open:
            self.close_keyboard()
            return False
        else:
            self.open_keyboard()
            return True

    def release(self) -> None:
        """Clean up — close keyboard if open."""
        if self._is_open:
            self.close_keyboard()

"""
NeuroTouch OS — Event Management & Debouncing
===============================================
Centralized cooldown tracking and event debouncing.
Uses timestamp-based cooldowns instead of time.sleep() to prevent blocking.
"""

import time
from typing import Dict
import config as cfg


class EventManager:
    """
    Manages action cooldowns to prevent repeated/accidental triggers.
    
    Each action type has an independent cooldown timer. Actions are only
    allowed when their cooldown has fully elapsed.
    """

    def __init__(self):
        # Last trigger timestamp for each action
        self._last_triggered: Dict[str, float] = {}

        # Cooldown durations per action (seconds)
        self._cooldowns: Dict[str, float] = {
            "left_click": cfg.COOLDOWN_LEFT_CLICK,
            "right_click": cfg.COOLDOWN_RIGHT_CLICK,
            "double_click": cfg.COOLDOWN_DOUBLE_CLICK,
            "hover_toggle": cfg.COOLDOWN_HOVER_TOGGLE,
            "voice_command": cfg.COOLDOWN_VOICE_COMMAND,
            "scroll": cfg.COOLDOWN_SCROLL,
            "keyboard_open": 1.5,
            "keyboard_close": 1.5,
        }

    def can_trigger(self, action: str) -> bool:
        """
        Check if an action's cooldown has elapsed.
        
        Args:
            action: Action identifier (e.g., "left_click", "right_click")
            
        Returns:
            True if the action can be triggered now
        """
        now = time.time()
        cooldown = self._cooldowns.get(action, 0.5)
        last = self._last_triggered.get(action, 0.0)
        return (now - last) >= cooldown

    def mark_triggered(self, action: str) -> None:
        """
        Record that an action was triggered at the current time.
        
        Args:
            action: Action identifier
        """
        self._last_triggered[action] = time.time()

    def try_trigger(self, action: str) -> bool:
        """
        Atomic check-and-mark: returns True and marks triggered if cooldown
        has elapsed, False otherwise.
        
        Args:
            action: Action identifier
            
        Returns:
            True if action was triggered, False if still in cooldown
        """
        if self.can_trigger(action):
            self.mark_triggered(action)
            return True
        return False

    def set_cooldown(self, action: str, duration: float) -> None:
        """
        Override the cooldown duration for a specific action.
        
        Args:
            action: Action identifier
            duration: Cooldown duration in seconds
        """
        self._cooldowns[action] = duration

    def reset(self, action: str = None) -> None:
        """
        Reset cooldown timer(s).
        
        Args:
            action: Specific action to reset, or None to reset all
        """
        if action:
            self._last_triggered.pop(action, None)
        else:
            self._last_triggered.clear()

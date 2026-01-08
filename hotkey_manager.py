"""
Hotkey Manager - Handles push-to-talk key detection

Uses keyboard library for better key suppression on Windows.
Supports configurable hotkeys.
"""

import keyboard
import threading
import time


# Map of key names to scan codes or keyboard library names
KEY_MAP = {
    "ctrl": "ctrl",
    "alt": "alt",
    "shift": "shift",
    "win": 91,  # Windows key scan code
    "space": "space",
    "tab": "tab",
    "caps": "caps lock",
    "f1": "f1",
    "f2": "f2",
    "f3": "f3",
    "f4": "f4",
    "f5": "f5",
    "f6": "f6",
    "f7": "f7",
    "f8": "f8",
    "f9": "f9",
    "f10": "f10",
    "f11": "f11",
    "f12": "f12",
}

# Display names for hotkeys
HOTKEY_OPTIONS = {
    "ctrl+win": "Ctrl + Win",
    "ctrl+alt": "Ctrl + Alt",
    "ctrl+shift": "Ctrl + Shift",
    "alt+shift": "Alt + Shift",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
}


class HotkeyManager:
    def __init__(self, on_press_callback, on_release_callback, hotkey="ctrl+win"):
        """
        Initialize the hotkey manager.

        Args:
            on_press_callback: Function to call when push-to-talk key is pressed
            on_release_callback: Function to call when push-to-talk key is released
            hotkey: Hotkey combination string (e.g., "ctrl+win", "f9")
        """
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
        self.hotkey = hotkey
        self.keys = self._parse_hotkey(hotkey)
        self.is_key_pressed = False
        self.running = False
        self.monitor_thread = None

    def _parse_hotkey(self, hotkey_str):
        """Parse hotkey string into list of keys."""
        parts = hotkey_str.lower().split("+")
        keys = []
        for part in parts:
            part = part.strip()
            if part in KEY_MAP:
                keys.append(KEY_MAP[part])
            else:
                keys.append(part)
        return keys

    def _check_keys(self):
        """Monitor thread that checks if hotkey is pressed."""
        while self.running:
            # Check if all keys in the hotkey are pressed
            all_pressed = True
            for key in self.keys:
                if isinstance(key, int):
                    # Scan code
                    if not keyboard.is_pressed(key):
                        all_pressed = False
                        break
                else:
                    # Key name
                    if not keyboard.is_pressed(key):
                        all_pressed = False
                        break

            if all_pressed and not self.is_key_pressed:
                # Keys just pressed
                self.is_key_pressed = True
                if self.on_press_callback:
                    self.on_press_callback()
            elif not all_pressed and self.is_key_pressed:
                # Keys just released
                self.is_key_pressed = False
                if self.on_release_callback:
                    self.on_release_callback()

            # Small sleep to prevent high CPU usage
            time.sleep(0.05)

    def start(self):
        """Start listening for hotkey events."""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._check_keys, daemon=True)
        self.monitor_thread.start()
        display_name = HOTKEY_OPTIONS.get(self.hotkey, self.hotkey.upper())
        print(f"Hotkey listener started. Hold '{display_name}' to record...")

    def stop(self):
        """Stop listening for hotkey events."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        keyboard.unhook_all()

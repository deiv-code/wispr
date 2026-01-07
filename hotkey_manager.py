"""
Hotkey Manager - Handles push-to-talk key detection

Uses keyboard library for better key suppression on Windows.
Hotkey: Ctrl + Windows key
"""

import keyboard
import threading
import time


class HotkeyManager:
    def __init__(self, on_press_callback, on_release_callback):
        """
        Initialize the hotkey manager.
        
        Args:
            on_press_callback: Function to call when push-to-talk key is pressed
            on_release_callback: Function to call when push-to-talk key is released
        """
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback
        self.is_key_pressed = False
        self.running = False
        self.monitor_thread = None

    def _check_keys(self):
        """Monitor thread that checks if both Ctrl and Windows are pressed."""
        while self.running:
            # Check if both Ctrl and Windows key are currently pressed
            ctrl_pressed = keyboard.is_pressed('ctrl')
            win_pressed = keyboard.is_pressed(91)  # Scan code for Windows key
            
            both_pressed = ctrl_pressed and win_pressed
            
            if both_pressed and not self.is_key_pressed:
                # Keys just pressed
                self.is_key_pressed = True
                if self.on_press_callback:
                    self.on_press_callback()
            elif not both_pressed and self.is_key_pressed:
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
        print("Hotkey listener started. Hold 'Ctrl+Windows' to record...")

    def stop(self):
        """Stop listening for hotkey events."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        keyboard.unhook_all()

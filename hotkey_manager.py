"""
Hotkey Manager - Handles push-to-talk key detection (6 key)

Uses the '6' key (vk: 54) as push-to-talk.
"""

from pynput import keyboard


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
        self.listener = None
        self.is_key_pressed = False
        
        # Target key: '6' with vk code 54
        self.target_vk = 54

    def _on_press(self, key):
        """Handle key press events."""
        # Check if this is our target key
        if self._is_target_key(key):
            if not self.is_key_pressed:
                self.is_key_pressed = True
                if self.on_press_callback:
                    self.on_press_callback()

    def _on_release(self, key):
        """Handle key release events."""
        # Check if this is our target key
        if self._is_target_key(key):
            if self.is_key_pressed:
                self.is_key_pressed = False
                if self.on_release_callback:
                    self.on_release_callback()

    def _is_target_key(self, key):
        """Check if the pressed key is our push-to-talk key ('6', vk: 54)."""
        try:
            # Check for character key '6'
            if hasattr(key, 'char') and key.char == '6':
                return True
            # Check for virtual key code 54
            vk = getattr(key, 'vk', None)
            if vk == self.target_vk:
                return True
        except:
            pass
        return False

    def start(self):
        """Start listening for hotkey events."""
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        print("Hotkey listener started. Hold '6' key to record...")

    def stop(self):
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None

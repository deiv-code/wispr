"""
Text Injector - Types or pastes text into the focused application
"""

import pyperclip
from pynput.keyboard import Controller, Key
from config import USE_CLIPBOARD


class TextInjector:
    def __init__(self):
        self.keyboard = Controller()

    def inject(self, text):
        """
        Inject text into the currently focused application.
        
        Uses clipboard paste for instant injection (USE_CLIPBOARD=True)
        or types character-by-character (USE_CLIPBOARD=False).
        """
        if not text:
            return

        if USE_CLIPBOARD:
            self._paste_text(text)
        else:
            self._type_text(text)

    def _paste_text(self, text):
        """Paste text using clipboard (instant)."""
        # Save current clipboard content
        try:
            old_clipboard = pyperclip.paste()
        except:
            old_clipboard = ""

        # Copy new text to clipboard
        pyperclip.copy(text)

        # Simulate Ctrl+V to paste
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('v')
        self.keyboard.release('v')
        self.keyboard.release(Key.ctrl)

        # Small delay then restore old clipboard (optional)
        # For now, we leave the transcribed text in clipboard
        # as user might want to paste it again

    def _type_text(self, text):
        """Type text character-by-character (slower but more compatible)."""
        self.keyboard.type(text)

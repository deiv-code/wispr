"""
Whisper - Sound Effects

Plays audio feedback sounds for recording start/stop.
Uses winsound for Windows native sound playback (no dependencies).
"""

from __future__ import annotations
import winsound
import threading
import os


class SoundEffects:
    """Handles playing sound effects for app feedback."""
    
    # Sound frequencies and durations for generated tones
    SOUNDS = {
        "start": {"freq": 800, "duration": 100},      # Higher pitch, short beep
        "stop": {"freq": 600, "duration": 100},       # Lower pitch, short beep  
        "success": {"freq": 1000, "duration": 150},   # High pitch for success
        "error": {"freq": 300, "duration": 200},      # Low pitch for error
    }
    
    def __init__(self, enabled=True):
        self.enabled = enabled
    
    def _play_tone(self, frequency: int, duration: int):
        """Play a tone in a separate thread (non-blocking)."""
        if not self.enabled:
            return
        
        def _play():
            try:
                winsound.Beep(frequency, duration)
            except:
                pass  # Ignore errors (e.g., no audio device)
        
        thread = threading.Thread(target=_play, daemon=True)
        thread.start()
    
    def play_start(self):
        """Play sound when recording starts."""
        sound = self.SOUNDS["start"]
        self._play_tone(sound["freq"], sound["duration"])
    
    def play_stop(self):
        """Play sound when recording stops."""
        sound = self.SOUNDS["stop"]
        self._play_tone(sound["freq"], sound["duration"])
    
    def play_success(self):
        """Play sound on successful transcription."""
        sound = self.SOUNDS["success"]
        self._play_tone(sound["freq"], sound["duration"])
    
    def play_error(self):
        """Play sound on error."""
        sound = self.SOUNDS["error"]
        self._play_tone(sound["freq"], sound["duration"])
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self.enabled = enabled


# Global instance
_sound_effects = None


def get_sound_effects() -> SoundEffects:
    """Get the global sound effects instance."""
    global _sound_effects
    if _sound_effects is None:
        _sound_effects = SoundEffects()
    return _sound_effects

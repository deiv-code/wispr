"""
WisprFlow - Settings Manager

Manages app settings with JSON persistence.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from threading import Lock


# Default settings
DEFAULT_SETTINGS = {
    "flow_bar_enabled": True,
    "sound_effects_enabled": True,
    "current_model": "base",
    "hotkey": "ctrl+win",  # For future customization
    "language": "en",      # Transcription language
}


class SettingsManager:
    """Manages application settings with persistence."""
    
    def __init__(self):
        # Store settings in user's app data folder
        self.data_dir = Path(os.path.expanduser("~")) / ".wisprflow"
        self.data_dir.mkdir(exist_ok=True)
        self.settings_file = self.data_dir / "settings.json"
        self.lock = Lock()
        
        # Load existing settings or create new
        self.settings = self._load_settings()
    
    def _load_settings(self) -> dict:
        """Load settings from JSON file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update(saved)
                    return merged
            except (json.JSONDecodeError, IOError):
                pass
        
        return DEFAULT_SETTINGS.copy()
    
    def _save_settings(self):
        """Save settings to JSON file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value and save."""
        with self.lock:
            self.settings[key] = value
            self._save_settings()
    
    def get_all(self) -> dict:
        """Get all settings."""
        return self.settings.copy()
    
    # Convenience properties
    @property
    def flow_bar_enabled(self) -> bool:
        return self.settings.get("flow_bar_enabled", True)
    
    @flow_bar_enabled.setter
    def flow_bar_enabled(self, value: bool):
        self.set("flow_bar_enabled", value)
    
    @property
    def sound_effects_enabled(self) -> bool:
        return self.settings.get("sound_effects_enabled", True)
    
    @sound_effects_enabled.setter
    def sound_effects_enabled(self, value: bool):
        self.set("sound_effects_enabled", value)
    
    @property
    def current_model(self) -> str:
        return self.settings.get("current_model", "base")
    
    @current_model.setter
    def current_model(self, value: str):
        self.set("current_model", value)
    
    @property
    def language(self) -> str:
        return self.settings.get("language", "en")
    
    @language.setter
    def language(self, value: str):
        self.set("language", value)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        with self.lock:
            self.settings = DEFAULT_SETTINGS.copy()
            self._save_settings()


# Global instance
_settings_manager = None


def get_settings() -> SettingsManager:
    """Get the global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

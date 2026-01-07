"""
Whisper - Stats Manager

Tracks transcription statistics and history with JSON persistence.
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from threading import Lock


class StatsManager:
    def __init__(self):
        # Store data in user's app data folder
        self.data_dir = Path(os.path.expanduser("~")) / ".wisprflow"
        self.data_dir.mkdir(exist_ok=True)
        self.stats_file = self.data_dir / "stats.json"
        self.lock = Lock()
        
        # Load existing stats or create new
        self.stats = self._load_stats()
    
    def _load_stats(self):
        """Load stats from JSON file."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Default stats structure
        return {
            "total_words": 0,
            "total_transcriptions": 0,
            "total_audio_seconds": 0.0,
            "history": [],  # List of transcription records
            "current_model": "base"
        }
    
    def _save_stats(self):
        """Save stats to JSON file."""
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving stats: {e}")
    
    def add_transcription(self, text: str, audio_duration: float, model: str):
        """
        Record a new transcription.
        
        Args:
            text: The transcribed text
            audio_duration: Duration of the audio in seconds
            model: The model used for transcription
        """
        if not text or not text.strip():
            return
        
        word_count = len(text.split())
        
        with self.lock:
            # Update totals
            self.stats["total_words"] += word_count
            self.stats["total_transcriptions"] += 1
            self.stats["total_audio_seconds"] += audio_duration
            
            # Add to history (keep last 100 entries)
            record = {
                "timestamp": datetime.now().isoformat(),
                "text": text.strip(),
                "word_count": word_count,
                "audio_duration": round(audio_duration, 1),
                "model": model
            }
            self.stats["history"].insert(0, record)
            
            # Limit history size
            if len(self.stats["history"]) > 100:
                self.stats["history"] = self.stats["history"][:100]
            
            self._save_stats()
    
    def get_total_words(self) -> int:
        """Get total words transcribed."""
        return self.stats["total_words"]
    
    def get_total_transcriptions(self) -> int:
        """Get total number of transcriptions."""
        return self.stats["total_transcriptions"]
    
    def get_total_audio_time(self) -> float:
        """Get total audio time in seconds."""
        return self.stats["total_audio_seconds"]
    
    def get_history(self, limit: int = 50) -> list:
        """Get transcription history."""
        return self.stats["history"][:limit]
    
    def get_current_model(self) -> str:
        """Get the currently selected model."""
        return self.stats.get("current_model", "base")
    
    def set_current_model(self, model: str):
        """Set the current model."""
        with self.lock:
            self.stats["current_model"] = model
            self._save_stats()
    
    def clear_history(self):
        """Clear transcription history but keep totals."""
        with self.lock:
            self.stats["history"] = []
            self._save_stats()
    
    def reset_all(self):
        """Reset all stats."""
        with self.lock:
            self.stats = {
                "total_words": 0,
                "total_transcriptions": 0,
                "total_audio_seconds": 0.0,
                "history": [],
                "current_model": self.stats.get("current_model", "tiny")
            }
            self._save_stats()


# Global instance
_stats_manager = None


def get_stats_manager() -> StatsManager:
    """Get the global stats manager instance."""
    global _stats_manager
    if _stats_manager is None:
        _stats_manager = StatsManager()
    return _stats_manager

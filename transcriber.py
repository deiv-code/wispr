"""
Transcriber - Whisper speech-to-text using faster-whisper

faster-whisper is a reimplementation of OpenAI's Whisper using CTranslate2,
which is much faster and works well on CPU.
"""

import numpy as np
from faster_whisper import WhisperModel
from config import WHISPER_THREADS


# Available models with descriptions
AVAILABLE_MODELS = {
    "1": ("tiny", "Tiny (~75MB) - Fastest, lower accuracy"),
    "2": ("base", "Base (~142MB) - Fast, decent accuracy"),
    "3": ("small", "Small (~466MB) - Medium speed, good accuracy"),
    "4": ("medium", "Medium (~1.5GB) - Slower, better accuracy"),
}


class Transcriber:
    def __init__(self, model_name="base"):
        self.model = None
        self.model_name = model_name

    def load_model(self):
        """Load the whisper model. Call once at startup."""
        print(f"Loading whisper model ({self.model_name})...")
        print("This may take a minute on first run (downloading model)...")
        
        self.model = WhisperModel(
            self.model_name,
            device="cpu",
            compute_type="int8",  # Use int8 for faster CPU inference
            cpu_threads=WHISPER_THREADS
        )
        print("Model loaded successfully!")

    def transcribe(self, audio_data):
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: numpy array of audio samples (float32, 16kHz, mono)
            
        Returns:
            Transcribed text string
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        if audio_data is None or len(audio_data) == 0:
            return ""

        try:
            # Ensure audio is float32 and normalized
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize if needed (should already be in range [-1, 1] from sounddevice)
            max_val = np.max(np.abs(audio_data))
            if max_val > 1.0:
                audio_data = audio_data / max_val
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio_data,
                beam_size=5,
                language="en",  # Set to None for auto-detection
                vad_filter=True,  # Filter out non-speech
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine all segments into a single text
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            
            text = ' '.join(text_parts)
            return text.strip()
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

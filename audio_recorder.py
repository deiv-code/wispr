"""
Audio Recorder - Captures microphone input using sounddevice
"""

import numpy as np
import sounddevice as sd
from config import SAMPLE_RATE, CHANNELS


class AudioRecorder:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.recording = False
        self.audio_buffer = []
        self.stream = None

    def _audio_callback(self, indata, frames, time, status):
        """Callback function called by sounddevice for each audio block."""
        if status:
            print(f"Audio status: {status}")
        if self.recording:
            self.audio_buffer.append(indata.copy())

    def start(self):
        """Start recording audio from the microphone."""
        self.audio_buffer = []
        self.recording = True
        
        try:
            # List available devices for debugging
            print(f"Default input device: {sd.default.device[0]}")
            
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                callback=self._audio_callback
            )
            self.stream.start()
            print("Audio stream started successfully")
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.recording = False

    def stop(self):
        """Stop recording and return the audio data as a numpy array."""
        self.recording = False
        
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"Error stopping stream: {e}")
            self.stream = None

        if not self.audio_buffer:
            print("Warning: No audio data captured!")
            return None

        # Concatenate all audio chunks into a single array
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        
        # Flatten to 1D array (mono)
        audio_data = audio_data.flatten()
        
        print(f"Captured {len(audio_data)} audio samples")
        
        return audio_data

    def is_recording(self):
        """Check if currently recording."""
        return self.recording

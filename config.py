"""
WisprFlow Clone - Configuration
"""

# Hotkey for push-to-talk (G6 key)
# Note: G6 is typically a macro key that may send a specific keycode
# We'll detect it via the keyboard listener
HOTKEY_NAME = "G6"

# Whisper model path
MODEL_PATH = r"C:\Users\David\desktop\whisper.cpp\models\ggml-medium.bin"

# Audio settings (required by whisper)
SAMPLE_RATE = 16000  # 16kHz
CHANNELS = 1         # Mono

# Performance settings
WHISPER_THREADS = 8  # Adjust based on your CPU cores

# Typing settings
USE_CLIPBOARD = True  # True = instant paste, False = character-by-character

# App name
APP_NAME = "WisprFlow Clone"

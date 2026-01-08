# Whisper

A push-to-talk voice dictation app for Windows. Hold a hotkey to record your voice, release to transcribe and paste the text into any application.

## Features

- Push-to-talk voice recording (Ctrl+Win)
- Fast local transcription using Whisper AI
- Automatic text injection into any focused application
- System tray icon with recording status
- Stats dashboard with transcription history
- Flow bar indicator during recording
- Sound effects for feedback
- Multiple Whisper model options (tiny, base, small, medium)

## Requirements

- Windows 10/11
- Python 3.9 or higher
- Microphone

## Installation

### 1. Clone or download the repository

```bash
git clone <repository-url>
cd wispr
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Note:** The first run will download the Whisper model (size depends on your selection).

### 4. Install Flet (for the GUI)

```bash
pip install flet==0.24.1
```

### 5. Create a desktop shortcut

Run the PowerShell script to create a desktop shortcut:

```powershell
powershell -ExecutionPolicy Bypass -File create_gui_shortcut.ps1
```

Or manually run the batch file:

```bash
create_shortcut.bat
```

## Usage

### Starting the app

**Option 1:** Double-click the "Whisper" shortcut on your desktop

**Option 2:** Run from command line:
```bash
python main.py
```

### Recording

1. Hold **Ctrl + Windows** key to start recording
2. Speak clearly into your microphone
3. Release the keys to stop recording
4. The transcribed text will be automatically typed into the focused application

### System Tray

- Right-click the tray icon to access the menu
- Click "Open Stats" to view transcription statistics and settings
- Click "Quit" to close the application

### Settings

Open the Stats window and go to the "Settings" tab to configure:

- **Whisper Model**: Choose between tiny, base, small, or medium models
  - Tiny: Fastest, lower accuracy (~75MB)
  - Base: Fast, decent accuracy (~142MB) - **Default**
  - Small: Medium speed, good accuracy (~466MB)
  - Medium: Slower, better accuracy (~1.5GB)
- **Flow Bar**: Toggle the floating recording indicator
- **Sound Effects**: Toggle audio feedback sounds

## File Structure

```
wispr/
├── main.py              # Main application entry point
├── audio_recorder.py    # Audio recording functionality
├── transcriber.py       # Whisper transcription
├── text_injector.py     # Text pasting/typing
├── hotkey_manager.py    # Keyboard hotkey handling
├── tray_icon.py         # System tray icon
├── stats_gui.py         # Flet-based stats dashboard
├── stats_manager.py     # Transcription statistics
├── settings_manager.py  # App settings persistence
├── flow_bar.py          # Recording indicator overlay
├── sound_effects.py     # Audio feedback
├── config.py            # Configuration constants
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Troubleshooting

### "Whisper is already running"
Close any existing instances from the system tray before starting a new one.

### No audio recorded
- Check your microphone is connected and set as the default recording device
- Check Windows sound settings

### Transcription is slow
- Try using a smaller model (tiny or base)
- Ensure no other heavy applications are running

### GUI shows error
- Make sure you have Flet 0.24.1 installed: `pip install flet==0.24.1`
- Python 3.9 users may experience issues with newer Flet versions

## Privacy & Data

- **Audio is never saved** - recordings are processed in memory and discarded
- **100% offline** - all transcription happens locally, nothing is sent to any server
- **Settings & history** stored in `~/.wisprflow/` (can be deleted anytime)
- **Whisper models** cached in `~/.cache/huggingface/` (75MB - 1.5GB depending on model)

## License

MIT License

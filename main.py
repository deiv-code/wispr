"""
Whisper Clone - Main Entry Point

A push-to-talk voice dictation tool that transcribes speech and types it
into any focused application.

Usage:
    python main.py

Controls:
    - Hold '6' key to record
    - Release to transcribe and type
    - Right-click tray icon to quit
"""

import sys
import os
import time
import threading
import subprocess
import tempfile
import atexit
from audio_recorder import AudioRecorder
from transcriber import Transcriber, AVAILABLE_MODELS
from text_injector import TextInjector
from hotkey_manager import HotkeyManager
from tray_icon import TrayIcon
from stats_manager import get_stats_manager
from settings_manager import get_settings
from flow_bar import get_flow_bar
from sound_effects import get_sound_effects


# Single instance lock file
LOCK_FILE = os.path.join(tempfile.gettempdir(), "wisprflow.lock")


def is_already_running():
    """Check if another instance is already running."""
    if os.path.exists(LOCK_FILE):
        # Check if the process is still alive
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            # Check if process exists (Windows)
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            if handle:
                kernel32.CloseHandle(handle)
                return True  # Process is still running
        except (ValueError, OSError, FileNotFoundError):
            pass  # Lock file is stale or invalid
    return False


def create_lock():
    """Create lock file with current PID."""
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_lock():
    """Remove lock file on exit."""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass


def select_model():
    """Display model selection menu and return chosen model name."""
    print("=" * 50)
    print("Whisper Clone - Model Selection")
    print("=" * 50)
    print()
    print("Available models:")
    print()
    for key, (name, description) in AVAILABLE_MODELS.items():
        print(f"  [{key}] {description}")
    print()
    
    while True:
        choice = input("Select model (1-4) [default: 1 for tiny]: ").strip()
        
        # Default to tiny
        if choice == "":
            choice = "1"
        
        if choice in AVAILABLE_MODELS:
            model_name, description = AVAILABLE_MODELS[choice]
            print(f"\nSelected: {description}")
            return model_name
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


class WhisperClone:
    def __init__(self, model_name="base"):
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber(model_name=model_name)
        self.text_injector = TextInjector()
        self.stats = get_stats_manager()
        self.settings = get_settings()
        self.model_name = model_name
        
        # Initialize flow bar and sound effects based on settings
        self.flow_bar = None
        self.sound_effects = None
        
        if self.settings.flow_bar_enabled:
            self.flow_bar = get_flow_bar()
            self.flow_bar.start()
        
        if self.settings.sound_effects_enabled:
            self.sound_effects = get_sound_effects()
        
        self.tray_icon = TrayIcon(
            on_quit_callback=self.shutdown,
            on_open_stats_callback=self.open_stats_gui
        )
        self.hotkey_manager = HotkeyManager(
            on_press_callback=self.on_record_start,
            on_release_callback=self.on_record_stop
        )
        self.running = True
        self.processing = False
        self.gui_process = None

    def open_stats_gui(self):
        """Open the stats GUI in a separate process."""
        try:
            # Launch stats GUI as separate process
            self.gui_process = subprocess.Popen(
                [sys.executable, "stats_gui.py"],
                cwd=sys.path[0] or "."
            )
        except Exception as e:
            print(f"Error opening stats GUI: {e}")

    def on_record_start(self):
        """Called when push-to-talk key is pressed."""
        if self.processing:
            return  # Don't start new recording while processing
            
        print("Recording started...")
        self.tray_icon.set_recording(True)
        
        # Show flow bar and play sound
        if self.flow_bar:
            self.flow_bar.show("Recording...")
        if self.sound_effects:
            self.sound_effects.play_start()
        
        self.audio_recorder.start()

    def on_record_stop(self):
        """Called when push-to-talk key is released."""
        if not self.audio_recorder.is_recording():
            return
            
        print("Recording stopped. Processing...")
        self.processing = True
        
        # Play stop sound and update flow bar
        if self.sound_effects:
            self.sound_effects.play_stop()
        if self.flow_bar:
            self.flow_bar.show_processing()
        
        # Stop recording and get audio data
        audio_data = self.audio_recorder.stop()
        
        if audio_data is not None and len(audio_data) > 0:
            # Transcribe in a separate thread to keep UI responsive
            threading.Thread(
                target=self._process_audio,
                args=(audio_data,),
                daemon=True
            ).start()
        else:
            print("No audio recorded.")
            self.tray_icon.set_recording(False)
            if self.flow_bar:
                self.flow_bar.hide()
            self.processing = False

    def _process_audio(self, audio_data):
        """Process audio data: transcribe and inject text."""
        try:
            # Calculate audio duration for info
            duration = len(audio_data) / 16000  # 16kHz sample rate
            print(f"Audio duration: {duration:.1f} seconds")
            
            # Transcribe
            print("Transcribing...")
            start_time = time.time()
            text = self.transcriber.transcribe(audio_data)
            elapsed = time.time() - start_time
            print(f"Transcription took {elapsed:.1f} seconds")
            
            if text:
                print(f"Transcribed: {text}")
                
                # Record stats
                word_count = len(text.split())
                self.stats.add_transcription(text, duration, self.model_name)
                
                # Show success on flow bar
                if self.flow_bar:
                    self.flow_bar.show_success(word_count)
                if self.sound_effects:
                    self.sound_effects.play_success()
                
                # Small delay to ensure the target window has focus
                time.sleep(0.1)
                # Inject the text
                self.text_injector.inject(text)
                print("Text injected!")
            else:
                print("No speech detected.")
                if self.flow_bar:
                    self.flow_bar.hide()
                
        except Exception as e:
            print(f"Error processing audio: {e}")
            if self.flow_bar:
                self.flow_bar.hide()
            if self.sound_effects:
                self.sound_effects.play_error()
        finally:
            self.tray_icon.set_recording(False)
            self.processing = False

    def shutdown(self):
        """Clean shutdown of all components."""
        print("Shutting down...")
        self.running = False
        self.hotkey_manager.stop()
        if self.flow_bar:
            self.flow_bar.stop()

    def run(self):
        """Main entry point - starts all components."""
        print()
        
        # Load the whisper model
        print("Initializing...")
        self.transcriber.load_model()
        print()
        
        # Start hotkey listener
        self.hotkey_manager.start()
        print()
        
        print("Ready! Hold 'Ctrl+Windows' to record, release to transcribe.")
        print("Right-click the tray icon to quit.")
        print()
        
        # Run tray icon in main thread (blocking)
        self.tray_icon.run()
        
        # Cleanup
        self.hotkey_manager.stop()
        print("Goodbye!")


def main():
    # Check for --auto flag (launched from GUI shortcut)
    auto_mode = "--auto" in sys.argv
    
    # Prevent multiple instances
    if is_already_running():
        print("Whisper is already running!")
        print("Check your system tray for the existing instance.")
        sys.exit(0)
    
    # Create lock file and register cleanup
    create_lock()
    atexit.register(remove_lock)
    
    if auto_mode:
        # Use saved model from settings
        settings = get_settings()
        model_name = settings.current_model
        print(f"Auto-starting with model: {model_name}")
    else:
        # Show model selection menu
        model_name = select_model()
    
    print()
    
    app = WhisperClone(model_name=model_name)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        app.shutdown()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        remove_lock()


if __name__ == "__main__":
    main()

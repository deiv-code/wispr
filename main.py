"""
WisprFlow Clone - Main Entry Point

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
import time
import threading
import subprocess
from audio_recorder import AudioRecorder
from transcriber import Transcriber, AVAILABLE_MODELS
from text_injector import TextInjector
from hotkey_manager import HotkeyManager
from tray_icon import TrayIcon
from stats_manager import get_stats_manager


def select_model():
    """Display model selection menu and return chosen model name."""
    print("=" * 50)
    print("WisprFlow Clone - Model Selection")
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


class WisprFlowClone:
    def __init__(self, model_name="tiny"):
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber(model_name=model_name)
        self.text_injector = TextInjector()
        self.stats = get_stats_manager()
        self.model_name = model_name
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
        self.audio_recorder.start()

    def on_record_stop(self):
        """Called when push-to-talk key is released."""
        if not self.audio_recorder.is_recording():
            return
            
        print("Recording stopped. Processing...")
        self.processing = True
        
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
                self.stats.add_transcription(text, duration, self.model_name)
                
                # Small delay to ensure the target window has focus
                time.sleep(0.1)
                # Inject the text
                self.text_injector.inject(text)
                print("Text injected!")
            else:
                print("No speech detected.")
                
        except Exception as e:
            print(f"Error processing audio: {e}")
        finally:
            self.tray_icon.set_recording(False)
            self.processing = False

    def shutdown(self):
        """Clean shutdown of all components."""
        print("Shutting down...")
        self.running = False
        self.hotkey_manager.stop()

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
    
    if auto_mode:
        # Use saved model from stats
        stats = get_stats_manager()
        model_name = stats.get_current_model()
        print(f"Auto-starting with model: {model_name}")
    else:
        # Show model selection menu
        model_name = select_model()
    
    print()
    
    app = WisprFlowClone(model_name=model_name)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        app.shutdown()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

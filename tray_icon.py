"""
System Tray Icon - Shows recording status in the Windows system tray
"""

import threading
from PIL import Image, ImageDraw
import pystray
from config import APP_NAME


class TrayIcon:
    def __init__(self, on_quit_callback=None):
        """
        Initialize the system tray icon.
        
        Args:
            on_quit_callback: Function to call when user clicks Quit
        """
        self.on_quit_callback = on_quit_callback
        self.icon = None
        self.is_recording = False
        
        # Create the icons
        self.icon_idle = self._create_icon(recording=False)
        self.icon_recording = self._create_icon(recording=True)

    def _create_icon(self, recording=False):
        """
        Create a simple microphone icon.
        
        Args:
            recording: If True, icon is red. If False, icon is gray.
        """
        # Create a 64x64 image
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Colors
        if recording:
            main_color = (220, 53, 69)  # Red
            accent_color = (255, 100, 100)
        else:
            main_color = (108, 117, 125)  # Gray
            accent_color = (150, 150, 150)
        
        # Draw microphone body (rounded rectangle)
        mic_left = 20
        mic_right = 44
        mic_top = 8
        mic_bottom = 38
        draw.rounded_rectangle(
            [mic_left, mic_top, mic_right, mic_bottom],
            radius=8,
            fill=main_color
        )
        
        # Draw microphone stand (arc)
        draw.arc(
            [14, 24, 50, 50],
            start=0,
            end=180,
            fill=main_color,
            width=4
        )
        
        # Draw microphone base (line)
        draw.line(
            [(32, 50), (32, 58)],
            fill=main_color,
            width=4
        )
        
        # Draw base horizontal line
        draw.line(
            [(22, 58), (42, 58)],
            fill=main_color,
            width=4
        )
        
        # Add recording indicator dot if recording
        if recording:
            draw.ellipse(
                [48, 4, 60, 16],
                fill=(255, 0, 0)
            )
        
        return image

    def _create_menu(self):
        """Create the right-click menu for the tray icon."""
        return pystray.Menu(
            pystray.MenuItem(
                "Status: Recording" if self.is_recording else "Status: Idle",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit)
        )

    def _on_quit(self, icon, item):
        """Handle quit menu item click."""
        icon.stop()
        if self.on_quit_callback:
            self.on_quit_callback()

    def set_recording(self, is_recording):
        """
        Update the icon to show recording status.
        
        Args:
            is_recording: True if recording, False if idle
        """
        self.is_recording = is_recording
        if self.icon:
            self.icon.icon = self.icon_recording if is_recording else self.icon_idle
            # Update menu to reflect new status
            self.icon.menu = self._create_menu()

    def run(self):
        """Start the system tray icon (blocking)."""
        self.icon = pystray.Icon(
            APP_NAME,
            self.icon_idle,
            APP_NAME,
            menu=self._create_menu()
        )
        self.icon.run()

    def run_detached(self):
        """Start the system tray icon in a separate thread (non-blocking)."""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()

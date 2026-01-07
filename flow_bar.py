"""
WisprFlow - Flow Bar

A minimal floating indicator that shows recording status.
Appears at the top of the screen when recording.
"""

from __future__ import annotations
import tkinter as tk
import threading
import time


class FlowBar:
    """A floating bar that indicates recording status."""
    
    def __init__(self):
        self.root = None
        self.label = None
        self.is_visible = False
        self.is_recording = False
        self.animation_running = False
        self.pulse_count = 0
        
        # Create UI in separate thread
        self._ui_thread = None
        self._ready = threading.Event()
        
    def _create_window(self):
        """Create the tkinter window."""
        self.root = tk.Tk()
        self.root.title("WisprFlow")
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Always on top
        self.root.attributes("-topmost", True)
        
        # Make window transparent (Windows)
        self.root.attributes("-transparentcolor", "black")
        
        # Window size and position (centered at top of screen)
        bar_width = 200
        bar_height = 36
        screen_width = self.root.winfo_screenwidth()
        x_position = (screen_width - bar_width) // 2
        y_position = 20  # 20px from top
        
        self.root.geometry(f"{bar_width}x{bar_height}+{x_position}+{y_position}")
        self.root.configure(bg="black")
        
        # Create frame with rounded corners effect
        self.frame = tk.Frame(
            self.root,
            bg="#1a1a2e",
            highlightbackground="#4a4a6a",
            highlightthickness=1
        )
        self.frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Recording indicator dot
        self.dot_canvas = tk.Canvas(
            self.frame,
            width=12,
            height=12,
            bg="#1a1a2e",
            highlightthickness=0
        )
        self.dot_canvas.pack(side=tk.LEFT, padx=(12, 6), pady=10)
        self.dot = self.dot_canvas.create_oval(2, 2, 10, 10, fill="#ff4757", outline="")
        
        # Label
        self.label = tk.Label(
            self.frame,
            text="Recording...",
            font=("Segoe UI", 11),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        self.label.pack(side=tk.LEFT, pady=8)
        
        # Start hidden
        self.root.withdraw()
        
        # Signal ready
        self._ready.set()
        
        # Start main loop
        self.root.mainloop()
    
    def start(self):
        """Start the flow bar UI thread."""
        self._ui_thread = threading.Thread(target=self._create_window, daemon=True)
        self._ui_thread.start()
        self._ready.wait(timeout=5)  # Wait for UI to be ready
    
    def _pulse_animation(self):
        """Animate the recording dot."""
        if not self.is_recording or not self.root:
            self.animation_running = False
            return
        
        self.animation_running = True
        self.pulse_count += 1
        
        # Pulse between bright red and darker red
        if self.pulse_count % 2 == 0:
            color = "#ff4757"  # Bright red
        else:
            color = "#c0392b"  # Darker red
        
        try:
            self.dot_canvas.itemconfig(self.dot, fill=color)
        except:
            pass
        
        # Continue animation
        if self.is_recording and self.root:
            self.root.after(500, self._pulse_animation)
        else:
            self.animation_running = False
    
    def show(self, text="Recording..."):
        """Show the flow bar."""
        if not self.root:
            return
            
        def _show():
            try:
                self.label.config(text=text)
                self.dot_canvas.itemconfig(self.dot, fill="#ff4757")
                self.root.deiconify()
                self.is_visible = True
                self.is_recording = True
                
                # Start pulse animation
                if not self.animation_running:
                    self._pulse_animation()
            except:
                pass
        
        self.root.after(0, _show)
    
    def update_text(self, text):
        """Update the flow bar text."""
        if not self.root or not self.label:
            return
            
        def _update():
            try:
                self.label.config(text=text)
            except:
                pass
        
        self.root.after(0, _update)
    
    def hide(self):
        """Hide the flow bar."""
        if not self.root:
            return
            
        def _hide():
            try:
                self.is_recording = False
                self.root.withdraw()
                self.is_visible = False
            except:
                pass
        
        self.root.after(0, _hide)
    
    def show_processing(self):
        """Show processing state."""
        if not self.root:
            return
            
        def _processing():
            try:
                self.is_recording = False
                self.label.config(text="Processing...")
                self.dot_canvas.itemconfig(self.dot, fill="#ffa502")  # Orange
            except:
                pass
        
        self.root.after(0, _processing)
    
    def show_success(self, word_count=0):
        """Show success state briefly."""
        if not self.root:
            return
            
        def _success():
            try:
                self.is_recording = False
                if word_count > 0:
                    self.label.config(text=f"Done! ({word_count} words)")
                else:
                    self.label.config(text="Done!")
                self.dot_canvas.itemconfig(self.dot, fill="#2ed573")  # Green
                # Hide after 1 second
                self.root.after(1000, self.hide)
            except:
                pass
        
        self.root.after(0, _success)
    
    def stop(self):
        """Stop and destroy the flow bar."""
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None


# Global instance
_flow_bar = None


def get_flow_bar() -> FlowBar:
    """Get the global flow bar instance."""
    global _flow_bar
    if _flow_bar is None:
        _flow_bar = FlowBar()
    return _flow_bar

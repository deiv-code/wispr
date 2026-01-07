"""
WisprFlow - Stats GUI

A minimal, modern Flet-based dashboard for viewing transcription stats and settings.
"""

from __future__ import annotations
import flet as ft
import asyncio
from datetime import datetime
from stats_manager import get_stats_manager
from settings_manager import get_settings
from transcriber import AVAILABLE_MODELS


class WisprFlowGUI:
    def __init__(self, on_model_change=None):
        """
        Initialize the GUI.
        
        Args:
            on_model_change: Callback when model is changed (receives model_name)
        """
        self.on_model_change = on_model_change
        self.stats = get_stats_manager()
        self.settings = get_settings()
        self.page = None
        
        # UI references for updating
        self.word_count_text = None
        self.transcription_count_text = None
        self.audio_time_text = None
        self.history_list = None
        self.model_dropdown = None
        
        # Settings UI references
        self.flow_bar_switch = None
        self.sound_effects_switch = None
        
        # For tracking changes
        self.last_transcription_count = 0
        self.refresh_running = False
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into readable time."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"
    
    def _format_timestamp(self, iso_timestamp: str) -> str:
        """Format ISO timestamp to readable format."""
        try:
            dt = datetime.fromisoformat(iso_timestamp)
            now = datetime.now()
            
            if dt.date() == now.date():
                return dt.strftime("Today %H:%M")
            elif (now.date() - dt.date()).days == 1:
                return dt.strftime("Yesterday %H:%M")
            else:
                return dt.strftime("%b %d, %H:%M")
        except:
            return iso_timestamp[:16]
    
    def _build_history_item(self, record: dict):
        """Build a history list item."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                self._format_timestamp(record["timestamp"]),
                                size=11,
                                color=ft.colors.GREY_500,
                            ),
                            ft.Text(
                                f"{record['word_count']} words",
                                size=11,
                                color=ft.colors.BLUE_400,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        record["text"],
                        size=13,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=4,
            ),
            padding=12,
            border_radius=8,
            bgcolor=ft.colors.GREY_900,
            margin=ft.margin.only(bottom=8),
        )
    
    def _refresh_stats(self):
        """Refresh all stats displays."""
        if self.word_count_text:
            self.word_count_text.value = str(self.stats.get_total_words())
        if self.transcription_count_text:
            self.transcription_count_text.value = str(self.stats.get_total_transcriptions())
        if self.audio_time_text:
            self.audio_time_text.value = self._format_time(self.stats.get_total_audio_time())
        if self.page:
            self.page.update()
    
    def _refresh_history(self):
        """Refresh the history list."""
        if self.history_list:
            self.history_list.controls.clear()
            history = self.stats.get_history(limit=50)
            
            if not history:
                self.history_list.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "No transcriptions yet.\nHold Ctrl+Win to record.",
                            size=14,
                            color=ft.colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        padding=40,
                        alignment=ft.alignment.center,
                    )
                )
            else:
                for record in history:
                    self.history_list.controls.append(
                        self._build_history_item(record)
                    )
            
            if self.page:
                self.page.update()
    
    def refresh(self):
        """Refresh all UI elements."""
        self._refresh_stats()
        self._refresh_history()
    
    async def _auto_refresh_loop(self):
        """Background task that refreshes stats every 2 seconds."""
        self.refresh_running = True
        while self.refresh_running:
            try:
                # Reload stats from disk to get latest data
                self.stats.stats = self.stats._load_stats()
                
                # Check if there are new transcriptions
                current_count = self.stats.get_total_transcriptions()
                if current_count != self.last_transcription_count:
                    self.last_transcription_count = current_count
                    self._refresh_stats()
                    self._refresh_history()
                
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Auto-refresh error: {e}")
                await asyncio.sleep(2)
    
    def _stop_refresh(self):
        """Stop the auto-refresh loop."""
        self.refresh_running = False
    
    def _on_model_changed(self, e):
        """Handle model dropdown change."""
        model_key = e.control.value
        if model_key in AVAILABLE_MODELS:
            model_name, _ = AVAILABLE_MODELS[model_key]
            self.settings.current_model = model_name
            
            if self.on_model_change:
                self.on_model_change(model_name)
            
            self._show_snackbar(f"Model changed to {model_name}. Restart to apply.")
    
    def _on_flow_bar_changed(self, e):
        """Handle flow bar toggle."""
        self.settings.flow_bar_enabled = e.control.value
        status = "enabled" if e.control.value else "disabled"
        self._show_snackbar(f"Flow bar {status}. Restart to apply.")
    
    def _on_sound_effects_changed(self, e):
        """Handle sound effects toggle."""
        self.settings.sound_effects_enabled = e.control.value
        status = "enabled" if e.control.value else "disabled"
        self._show_snackbar(f"Sound effects {status}. Restart to apply.")
    
    def _show_snackbar(self, message: str):
        """Show a snackbar message."""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.BLUE_900,
                open=True,
            )
            self.page.update()
    
    def _get_model_key(self, model_name: str) -> str:
        """Get model key from model name."""
        for key, (name, _) in AVAILABLE_MODELS.items():
            if name == model_name:
                return key
        return "2"  # Default to base
    
    def _build_stats_tab(self):
        """Build the Stats tab content."""
        # Get current stats
        total_words = self.stats.get_total_words()
        total_transcriptions = self.stats.get_total_transcriptions()
        total_time = self.stats.get_total_audio_time()
        
        # Build stat cards with references
        self.word_count_text = ft.Text(str(total_words), size=28, weight=ft.FontWeight.BOLD)
        self.transcription_count_text = ft.Text(str(total_transcriptions), size=28, weight=ft.FontWeight.BOLD)
        self.audio_time_text = ft.Text(self._format_time(total_time), size=28, weight=ft.FontWeight.BOLD)
        
        word_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.TEXT_FIELDS, size=24, color=ft.colors.BLUE_400),
                    self.word_count_text,
                    ft.Text("Words", size=11, color=ft.colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=16,
            border_radius=12,
            bgcolor=ft.colors.GREY_900,
            expand=True,
        )
        
        transcription_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.MIC, size=24, color=ft.colors.GREEN_400),
                    self.transcription_count_text,
                    ft.Text("Sessions", size=11, color=ft.colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=16,
            border_radius=12,
            bgcolor=ft.colors.GREY_900,
            expand=True,
        )
        
        time_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.TIMER, size=24, color=ft.colors.ORANGE_400),
                    self.audio_time_text,
                    ft.Text("Audio", size=11, color=ft.colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=16,
            border_radius=12,
            bgcolor=ft.colors.GREY_900,
            expand=True,
        )
        
        # History list
        self.history_list = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )
        
        # Populate history
        self._refresh_history()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Stats row
                    ft.Row(
                        controls=[word_card, transcription_card, time_card],
                        spacing=10,
                    ),
                    
                    # History section
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text("History", size=14, weight=ft.FontWeight.W_500),
                                        ft.TextButton(
                                            "Clear",
                                            on_click=lambda e: self._clear_history(),
                                            style=ft.ButtonStyle(color=ft.colors.GREY_500),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Container(
                                    content=self.history_list,
                                    expand=True,
                                    border_radius=12,
                                ),
                            ],
                            spacing=8,
                            expand=True,
                        ),
                        expand=True,
                        padding=ft.padding.only(top=16),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            padding=16,
            expand=True,
        )
    
    def _build_settings_tab(self):
        """Build the Settings tab content."""
        current_model = self.settings.current_model
        
        # Model dropdown
        self.model_dropdown = ft.Dropdown(
            value=self._get_model_key(current_model),
            options=[
                ft.dropdown.Option(key, desc)
                for key, (name, desc) in AVAILABLE_MODELS.items()
            ],
            on_change=self._on_model_changed,
            border_radius=8,
            content_padding=12,
            bgcolor=ft.colors.GREY_900,
        )
        
        # Flow bar toggle
        self.flow_bar_switch = ft.Switch(
            value=self.settings.flow_bar_enabled,
            on_change=self._on_flow_bar_changed,
            active_color=ft.colors.BLUE_400,
        )
        
        # Sound effects toggle
        self.sound_effects_switch = ft.Switch(
            value=self.settings.sound_effects_enabled,
            on_change=self._on_sound_effects_changed,
            active_color=ft.colors.BLUE_400,
        )
        
        def build_setting_row(title, subtitle, control):
            """Build a setting row with title, subtitle, and control."""
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                                ft.Text(subtitle, size=11, color=ft.colors.GREY_500),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        control,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=16,
                border_radius=12,
                bgcolor=ft.colors.GREY_900,
                margin=ft.margin.only(bottom=10),
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Model selection
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("Whisper Model", size=14, weight=ft.FontWeight.W_500),
                                ft.Text("Larger models are more accurate but slower", size=11, color=ft.colors.GREY_500),
                                ft.Container(
                                    content=self.model_dropdown,
                                    padding=ft.padding.only(top=8),
                                ),
                            ],
                            spacing=2,
                        ),
                        padding=16,
                        border_radius=12,
                        bgcolor=ft.colors.GREY_900,
                        margin=ft.margin.only(bottom=10),
                    ),
                    
                    # Flow bar toggle
                    build_setting_row(
                        "Flow Bar",
                        "Show floating indicator when recording",
                        self.flow_bar_switch,
                    ),
                    
                    # Sound effects toggle
                    build_setting_row(
                        "Sound Effects",
                        "Play sounds on record start/stop",
                        self.sound_effects_switch,
                    ),
                    
                    # Hotkey info (read-only for now)
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text("Hotkey", size=14, weight=ft.FontWeight.W_500),
                                        ft.Text("Press and hold to record", size=11, color=ft.colors.GREY_500),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text("Ctrl + Win", size=13, color=ft.colors.BLUE_400),
                                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                    border_radius=6,
                                    bgcolor=ft.colors.GREY_800,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=16,
                        border_radius=12,
                        bgcolor=ft.colors.GREY_900,
                        margin=ft.margin.only(bottom=10),
                    ),
                    
                    # Version info
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("WisprFlow", size=12, color=ft.colors.GREY_500),
                                ft.Text("Version 1.0.0", size=11, color=ft.colors.GREY_600),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2,
                        ),
                        padding=20,
                        alignment=ft.alignment.center,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=16,
            expand=True,
        )
    
    def main(self, page: ft.Page):
        """Main Flet app entry point."""
        self.page = page
        
        # Page settings
        page.title = "WisprFlow"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.window.width = 400
        page.window.height = 580
        page.window.resizable = True
        page.window.min_width = 350
        page.window.min_height = 500
        
        # Stop refresh when window closes
        def on_window_event(e):
            if e.data == "close":
                self._stop_refresh()
        
        page.window.on_event = on_window_event
        
        # Initialize tracking
        self.last_transcription_count = self.stats.get_total_transcriptions()
        
        # Start auto-refresh background task
        page.run_task(self._auto_refresh_loop)
        
        # Build tabs
        stats_tab = ft.Tab(
            text="Stats",
            content=self._build_stats_tab(),
        )
        
        settings_tab = ft.Tab(
            text="Settings",
            content=self._build_settings_tab(),
        )
        
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[stats_tab, settings_tab],
            expand=True,
        )
        
        # Build layout
        page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Header
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.icons.GRAPHIC_EQ, size=24, color=ft.colors.BLUE_400),
                                    ft.Text("WisprFlow", size=20, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
                        ),
                        
                        # Tabs
                        tabs,
                    ],
                    spacing=0,
                    expand=True,
                ),
                expand=True,
                bgcolor=ft.colors.BLACK,
            )
        )
    
    def _clear_history(self):
        """Clear history after confirmation."""
        if self.page:
            def close_dialog(e):
                dialog.open = False
                self.page.update()
            
            def confirm_clear(e):
                self.stats.clear_history()
                self._refresh_history()
                dialog.open = False
                self.page.update()
            
            dialog = ft.AlertDialog(
                title=ft.Text("Clear History?"),
                content=ft.Text("This will delete all transcription history. Stats totals will be kept."),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dialog),
                    ft.TextButton("Clear", on_click=confirm_clear),
                ],
            )
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()


def run_gui(on_model_change=None):
    """Run the GUI as a standalone app."""
    gui = WisprFlowGUI(on_model_change=on_model_change)
    ft.app(target=gui.main)


if __name__ == "__main__":
    run_gui()

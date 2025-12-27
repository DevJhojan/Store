"""Utilidad para crear tooltips en widgets."""
import tkinter as tk

from ...config.settings import Settings, COLORS


def create_tooltip(widget: tk.Widget, text: str):
    """
    Crea un tooltip para un widget.
    
    Args:
        widget: Widget al que se le agregará el tooltip
        text: Texto del tooltip
    """
    c = COLORS
    
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = tk.Label(
            tooltip,
            text=text,
            background=c["bg_medium"],
            foreground=c["text_primary"],
            relief=tk.SOLID,
            borderwidth=1,
            font=(Settings.FONT_PRIMARY, 9),
            padx=5,
            pady=3
        )
        label.pack()
        widget.tooltip = tooltip
    
    def on_leave(event):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            del widget.tooltip
    
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


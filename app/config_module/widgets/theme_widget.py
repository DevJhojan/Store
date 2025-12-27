"""Widget para cambio de tema."""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from ...config.settings import Settings, COLORS


def create_theme_widget(parent: tk.Frame, on_theme_change: Callable) -> tk.Frame:
    """
    Crea el widget de cambio de tema.
    
    Args:
        parent: Frame padre
        on_theme_change: Callback cuando se cambia el tema
        
    Returns:
        Frame del widget de tema
    """
    c = COLORS
    
    theme_frame = tk.Frame(parent, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
    theme_frame.pack(fill=tk.X, padx=15, pady=15)
    
    # Título
    theme_title = tk.Label(
        theme_frame,
        text="► Cambio de Tema",
        font=(Settings.FONT_PRIMARY, 12, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"],
        pady=10
    )
    theme_title.pack(anchor="w", padx=15, pady=(10, 5))
    
    # Frame para contenido
    theme_content = tk.Frame(theme_frame, bg=c["bg_dark"])
    theme_content.pack(fill=tk.X, padx=15, pady=(0, 15))
    
    # Label y combobox para tema
    theme_label = tk.Label(
        theme_content,
        text="Seleccione un tema:",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_dark"]
    )
    theme_label.pack(side=tk.LEFT, padx=(0, 10))
    
    theme_combo = ttk.Combobox(
        theme_content,
        values=["Dark", "Light"],
        state="readonly",
        width=20
    )
    theme_combo.pack(side=tk.LEFT, padx=(0, 10))
    # El tema se establecerá desde la vista principal
    
    # Botón aplicar tema
    btn_aplicar_tema = ttk.Button(
        theme_content,
        text="Aplicar Tema",
        command=lambda: on_theme_change(theme_combo.get()),
        style="Accent.TButton"
    )
    btn_aplicar_tema.pack(side=tk.LEFT)
    
    # Guardar referencia al combobox para acceso externo
    theme_frame.theme_combo = theme_combo
    
    return theme_frame


"""Widget para gestión de información de tienda."""
import tkinter as tk
from typing import Dict, Callable

from ...config.settings import Settings, COLORS


def create_tienda_widget(parent: tk.Frame, on_save: Callable) -> Dict[str, tk.Widget]:
    """
    Crea el widget de información de tienda.
    
    Args:
        parent: Frame padre
        on_save: Callback cuando se guarda la información
        
    Returns:
        Dict con las referencias a los widgets
    """
    c = COLORS
    
    # Frame principal con borde y separación
    tienda_frame = tk.Frame(parent, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
    tienda_frame.pack(fill=tk.X, padx=15, pady=15)
    
    # Título de la sección
    tienda_title = tk.Label(
        tienda_frame,
        text="► Información de la Tienda",
        font=(Settings.FONT_PRIMARY, 12, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"],
        pady=10
    )
    tienda_title.pack(anchor="w", padx=15, pady=(10, 5))
    
    # Frame para contenido
    content_frame = tk.Frame(tienda_frame, bg=c["bg_dark"])
    content_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
    
    widgets = {}
    
    # Nombre de la tienda
    nombre_label = tk.Label(
        content_frame,
        text="Nombre de la tienda:",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_dark"]
    )
    nombre_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
    
    widgets["nombre"] = tk.Entry(
        content_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"],
        width=40
    )
    widgets["nombre"].grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
    
    # Descripción de la tienda
    descripcion_label = tk.Label(
        content_frame,
        text="Descripción:",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_dark"]
    )
    descripcion_label.grid(row=1, column=0, sticky="nw", padx=(0, 10), pady=5)
    
    widgets["descripcion"] = tk.Text(
        content_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"],
        width=40,
        height=4,
        wrap=tk.WORD
    )
    widgets["descripcion"].grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)
    
    # Configurar columnas para que se expandan
    content_frame.grid_columnconfigure(1, weight=1)
    
    # Botón guardar
    btn_guardar = tk.Button(
        content_frame,
        text="Guardar Información",
        command=on_save,
        font=(Settings.FONT_PRIMARY, 10, "bold"),
        bg=c["red_primary"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        padx=20,
        pady=8,
        cursor="hand2"
    )
    btn_guardar.grid(row=2, column=0, columnspan=2, pady=(10, 0))
    
    return widgets


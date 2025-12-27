"""Widget del panel lateral para mostrar el código del producto."""
import tkinter as tk
from typing import Dict

from ...config.settings import Settings, COLORS


def create_lateral_panel(parent: tk.Frame) -> Dict[str, tk.Entry]:
    """
    Crea el panel lateral izquierdo para mostrar el código.
    
    Args:
        parent: Frame padre
        
    Returns:
        Dict con la referencia al entry del código lateral
    """
    c = COLORS
    
    lateral_frame = tk.Frame(parent, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
    lateral_frame.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(0, 10), pady=0)
    lateral_frame.grid_propagate(False)
    lateral_frame.config(width=200)
    
    # Título del panel lateral
    lateral_title = tk.Label(
        lateral_frame,
        text="Código",
        font=(Settings.FONT_PRIMARY, 12, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"],
        pady=15
    )
    lateral_title.pack()
    
    # Información sobre código autoincremental
    info_label = tk.Label(
        lateral_frame,
        text="Código auto\nincrementable,\nno editable",
        font=(Settings.FONT_PRIMARY, 9),
        fg=c["text_secondary"],
        bg=c["bg_dark"],
        justify=tk.CENTER,
        wraplength=180,
        pady=10
    )
    info_label.pack()
    
    # Campo código (solo lectura)
    codigo_lateral = tk.Entry(
        lateral_frame,
        font=(Settings.FONT_PRIMARY, 14, "bold"),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        state="readonly",
        justify=tk.CENTER,
        readonlybackground=c["bg_medium"]
    )
    codigo_lateral.pack(fill=tk.X, padx=15, pady=10)
    
    return {"codigo_lateral": codigo_lateral}


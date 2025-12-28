"""Widget del resumen total de productos."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable

from ...config.settings import Settings, COLORS
from ..utils.tooltip import create_tooltip


def create_summary_widget(parent: tk.Frame, on_recalculate: Callable) -> Dict[str, tk.Label]:
    """
    Crea el widget de resumen total.
    
    Args:
        parent: Frame padre
        on_recalculate: Función callback para recalcular
        
    Returns:
        Dict con las referencias a los labels del resumen
    """
    c = COLORS
    
    summary_frame = tk.Frame(parent, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
    summary_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
    summary_frame.grid_columnconfigure(1, weight=1)  # El contenido toma el espacio
    
    # Frame para botón y título
    summary_header = tk.Frame(summary_frame, bg=c["bg_dark"])
    summary_header.pack(fill=tk.X, padx=15, pady=15)
    
    # Botón Recalcular (solo icono, a la izquierda)
    btn_recalcular = ttk.Button(
        summary_header,
        text="[ Actualizar ]",
        command=on_recalculate,
        style="Accent.TButton"
    )
    btn_recalcular.pack(side=tk.LEFT, padx=(0, 10))
    
    # Tooltip para el botón
    create_tooltip(btn_recalcular, "Recalcular datos")
    
    # Título del resumen
    summary_title = tk.Label(
        summary_header,
        text="Resumen Total",
        font=(Settings.FONT_PRIMARY, 12, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"]
    )
    summary_title.pack(side=tk.LEFT)
    
    # Contenedor de resumen
    summary_content = tk.Frame(summary_frame, bg=c["bg_dark"])
    summary_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
    
    # Labels de resumen
    labels = {}
    
    labels["total_productos"] = tk.Label(
        summary_content,
        text="Total Productos: 0",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_dark"],
        anchor=tk.W
    )
    labels["total_productos"].pack(fill=tk.X, pady=(0, 10))
    
    labels["valor_total_base"] = tk.Label(
        summary_content,
        text="Valor Total Base: $0.00",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_dark"],
        anchor=tk.W
    )
    labels["valor_total_base"].pack(fill=tk.X, pady=(0, 10))
    
    labels["valor_total_ganancia"] = tk.Label(
        summary_content,
        text="Valor Total Ganancia: $0.00",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_dark"],
        anchor=tk.W
    )
    labels["valor_total_ganancia"].pack(fill=tk.X, pady=(0, 10))
    
    # Separador
    separator = tk.Frame(summary_content, bg=c["red_primary"], height=2)
    separator.pack(fill=tk.X, pady=15)
    
    labels["valor_total_subtotal"] = tk.Label(
        summary_content,
        text="TOTAL: $0.00",
        font=(Settings.FONT_PRIMARY, 12, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"],
        anchor=tk.W
    )
    labels["valor_total_subtotal"].pack(fill=tk.X, pady=(10, 0))
    
    return labels


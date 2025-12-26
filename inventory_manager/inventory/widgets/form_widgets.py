"""Widgets del formulario de producto."""
import tkinter as tk
from typing import Dict, Optional, Callable

from ...config.settings import Settings, COLORS


def create_form_widgets(
    parent: tk.Frame,
    on_calculo_change: Optional[Callable] = None
) -> Dict[str, tk.Entry]:
    """
    Crea los widgets del formulario de producto.
    
    Args:
        parent: Frame padre
        on_calculo_change: Callback opcional para cuando cambian los campos de cálculo
        
    Returns:
        Dict con las referencias a los entries del formulario
    """
    c = COLORS
    
    form_frame = tk.Frame(parent, bg=c["bg_darkest"])
    form_frame.grid(row=0, column=1, sticky="ew", padx=0, pady=(0, 15))
    form_frame.grid_columnconfigure(0, weight=1)
    form_frame.grid_columnconfigure(1, weight=1)
    form_frame.grid_columnconfigure(2, weight=1)
    
    entries: Dict[str, tk.Entry] = {}
    
    # Fila 1: Código, Nombre, Categoría
    # Código (sincronizado con panel lateral)
    codigo_label = tk.Label(
        form_frame,
        text="Código",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    codigo_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
    
    entries["codigo"] = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        state="readonly",
        readonlybackground=c["bg_medium"]
    )
    entries["codigo"].grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))
    
    # Nombre
    nombre_label = tk.Label(
        form_frame,
        text="Nombre",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    nombre_label.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(0, 5))
    
    entries["nombre"] = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"]
    )
    entries["nombre"].grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))
    
    # Categoría
    categoria_label = tk.Label(
        form_frame,
        text="Categoría",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    categoria_label.grid(row=0, column=2, sticky="w", padx=0, pady=(0, 5))
    
    entries["categoria"] = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"]
    )
    entries["categoria"].grid(row=1, column=2, sticky="ew", padx=0, pady=(0, 15))
    
    # Fila 2: Cantidad, Precio unitario, Ganancia
    # Cantidad
    cantidad_label = tk.Label(
        form_frame,
        text="Cantidad",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    cantidad_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
    
    entries["cantidad"] = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"]
    )
    entries["cantidad"].grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 0))
    
    # Precio unitario
    precio_label = tk.Label(
        form_frame,
        text="Precio unitario",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    precio_label.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=(0, 5))
    
    entries["precio_unitario"] = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"]
    )
    entries["precio_unitario"].grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=(0, 0))
    
    # Ganancia (%)
    ganancia_label = tk.Label(
        form_frame,
        text="Ganancia (%)",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    ganancia_label.grid(row=2, column=2, sticky="w", padx=0, pady=(0, 5))
    
    ganancia_entry = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"]
    )
    ganancia_entry.grid(row=3, column=2, sticky="ew", padx=0, pady=(0, 0))
    ganancia_entry.insert(0, "0")
    
    # Vincular eventos para cálculo automático
    if on_calculo_change:
        entries["cantidad"].bind("<KeyRelease>", on_calculo_change)
        entries["precio_unitario"].bind("<KeyRelease>", on_calculo_change)
        ganancia_entry.bind("<KeyRelease>", on_calculo_change)
    
    return entries, ganancia_entry


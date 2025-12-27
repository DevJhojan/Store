"""Widget de la barra de botones de acciones."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable

from ...config.settings import COLORS


def create_button_bar(
    parent: tk.Frame,
    on_add: Callable,
    on_update: Callable,
    on_delete: Callable,
    on_clear: Callable
) -> tk.Frame:
    """
    Crea la barra de botones de acciones.
    
    Args:
        parent: Frame padre
        on_add: Callback para agregar producto
        on_update: Callback para actualizar producto
        on_delete: Callback para eliminar producto
        on_clear: Callback para limpiar formulario
        
    Returns:
        Frame contenedor de los botones
    """
    c = COLORS
    
    buttons_frame = tk.Frame(parent, bg=c["bg_darkest"])
    buttons_frame.grid(row=1, column=1, sticky="ew", padx=0, pady=(0, 15))
    
    btn_agregar = ttk.Button(
        buttons_frame,
        text="➕ Agregar",
        command=on_add,
        style="Accent.TButton"
    )
    btn_agregar.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_actualizar = ttk.Button(
        buttons_frame,
        text="✏️ Actualizar",
        command=on_update,
        style="Accent.TButton"
    )
    btn_actualizar.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_eliminar = ttk.Button(
        buttons_frame,
        text="🗑️ Eliminar",
        command=on_delete,
        style="Accent.TButton"
    )
    btn_eliminar.pack(side=tk.LEFT, padx=(0, 10))
    
    btn_limpiar = ttk.Button(
        buttons_frame,
        text="🧹 Limpiar",
        command=on_clear,
        style="Secondary.TButton"
    )
    btn_limpiar.pack(side=tk.LEFT)
    
    return buttons_frame


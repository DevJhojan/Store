"""Widget para gestión de categorías."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable

from ...config.settings import Settings, COLORS


def create_categoria_form_widget(parent: tk.Frame) -> Dict[str, tk.Widget]:
    """
    Crea el widget del formulario de categoría.
    
    Args:
        parent: Frame padre
        
    Returns:
        Dict con las referencias a los widgets del formulario
    """
    c = COLORS
    
    form_frame = tk.Frame(parent, bg=c["bg_darkest"])
    form_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
    
    widgets = {}
    
    # Nombre
    nombre_label = tk.Label(
        form_frame,
        text="Nombre:",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    nombre_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
    
    widgets["nombre"] = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"]
    )
    widgets["nombre"].grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
    
    # Descripción
    descripcion_label = tk.Label(
        form_frame,
        text="Descripción:",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_darkest"]
    )
    descripcion_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
    
    widgets["descripcion"] = tk.Entry(
        form_frame,
        font=(Settings.FONT_PRIMARY, 11),
        bg=c["bg_medium"],
        fg=c["text_primary"],
        relief=tk.FLAT,
        insertbackground=c["text_primary"]
    )
    widgets["descripcion"].grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)
    
    # Configurar columnas
    form_frame.grid_columnconfigure(1, weight=1)
    
    return widgets


def create_categoria_buttons_widget(parent: tk.Frame, on_add: Callable, 
                                   on_update: Callable, on_delete: Callable,
                                   on_clear: Callable) -> tk.Frame:
    """
    Crea el widget de botones para categorías.
    
    Args:
        parent: Frame padre
        on_add: Callback para agregar
        on_update: Callback para actualizar
        on_delete: Callback para eliminar
        on_clear: Callback para limpiar
        
    Returns:
        Frame de botones
    """
    c = COLORS
    
    buttons_frame = tk.Frame(parent, bg=c["bg_darkest"])
    buttons_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
    
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


def create_categoria_summary_widget(parent: tk.Frame) -> Dict[str, tk.Label]:
    """
    Crea el widget de resumen de categoría.
    
    Args:
        parent: Frame padre
        
    Returns:
        Dict con las referencias a los labels del resumen
    """
    c = COLORS
    
    from ...config.settings import Settings
    
    # Frame para resumen
    summary_frame = tk.Frame(parent, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
    summary_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
    
    # Título del resumen
    summary_title = tk.Label(
        summary_frame,
        text="Resumen de ''",
        font=(Settings.FONT_PRIMARY, 14, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"],
        pady=10
    )
    summary_title.pack(anchor="w", padx=15, pady=(10, 5))
    
    # Descripción
    summary_desc = tk.Label(
        summary_frame,
        text="",
        font=(Settings.FONT_PRIMARY, 10),
        fg=c["text_secondary"],
        bg=c["bg_dark"],
        wraplength=600,
        justify=tk.LEFT
    )
    summary_desc.pack(anchor="w", padx=15, pady=(0, 10))
    
    return {
        "title": summary_title,
        "description": summary_desc
    }


def create_categoria_table_widget(parent: tk.Frame) -> ttk.Treeview:
    """
    Crea el widget de tabla para mostrar categorías.
    
    Args:
        parent: Frame padre
        
    Returns:
        Treeview configurado para mostrar categorías
    """
    c = COLORS
    
    from ...config.settings import Settings
    
    # Frame para tabla
    table_frame = tk.Frame(parent, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
    table_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
    table_frame.grid_rowconfigure(1, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    
    # Título
    table_title = tk.Label(
        table_frame,
        text="► Categorías",
        font=(Settings.FONT_PRIMARY, 12, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"],
        pady=10
    )
    table_title.grid(row=0, column=0, sticky="ew", padx=15)
    
    # Frame para tabla con scrollbar
    table_container = tk.Frame(table_frame, bg=c["bg_dark"])
    table_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=1)
    
    # Scrollbar
    v_scrollbar = ttk.Scrollbar(
        table_container,
        orient=tk.VERTICAL,
        style="Custom.Vertical.TScrollbar"
    )
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    
    # Treeview
    columns = ("id", "nombre", "descripcion")
    tree = ttk.Treeview(
        table_container,
        columns=columns,
        show="headings",
        style="Custom.Treeview",
        yscrollcommand=v_scrollbar.set,
        height=15
    )
    
    v_scrollbar.config(command=tree.yview)
    tree.grid(row=0, column=0, sticky="nsew")
    
    # Configurar columnas
    tree.heading("id", text="ID")
    tree.heading("nombre", text="Nombre")
    tree.heading("descripcion", text="Descripción")
    
    tree.column("id", width=50, anchor=tk.CENTER)
    tree.column("nombre", width=200, anchor=tk.W)
    tree.column("descripcion", width=300, anchor=tk.W)
    
    return tree


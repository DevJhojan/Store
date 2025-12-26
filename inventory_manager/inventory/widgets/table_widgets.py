"""Widget de la tabla de productos."""
import tkinter as tk
from tkinter import ttk

from ...config.settings import COLORS


def create_table_widget(parent: tk.Frame) -> ttk.Treeview:
    """
    Crea el widget de tabla para mostrar los productos.
    
    Args:
        parent: Frame padre
        
    Returns:
        Treeview configurado para mostrar productos
    """
    c = COLORS
    
    from ...config.settings import Settings
    
    # Tabla de datos (arriba, ancho completo)
    table_frame = tk.Frame(parent, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
    table_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 10))
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_rowconfigure(1, weight=1)  # Permitir que la tabla se expanda
    
    table_title = tk.Label(
        table_frame,
        text="Tabla de datos",
        font=(Settings.FONT_PRIMARY, 12, "bold"),
        fg=c["red_primary"],
        bg=c["bg_dark"],
        pady=10
    )
    table_title.grid(row=0, column=0, sticky="ew")
    
    # Frame para tabla con scrollbars usando grid para mejor control
    table_container = tk.Frame(table_frame, bg=c["bg_dark"])
    table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=1)
    
    # Scrollbar vertical estilizada
    v_scrollbar = ttk.Scrollbar(
        table_container,
        orient=tk.VERTICAL,
        style="Custom.Vertical.TScrollbar"
    )
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    
    # Scrollbar horizontal estilizada
    h_scrollbar = ttk.Scrollbar(
        table_container,
        orient=tk.HORIZONTAL,
        style="Custom.Horizontal.TScrollbar"
    )
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    # Treeview (tabla) - sin height fijo para que sea dinámico
    columns = ("codigo", "nombre", "categoria", "cantidad", "precio_unitario", 
              "ganancia_unit", "valor_venta", "valor_base", "valor_ganancia", "subtotal")
    
    tree = ttk.Treeview(
        table_container,
        columns=columns,
        show="headings",
        style="Custom.Treeview",
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    
    v_scrollbar.config(command=tree.yview)
    h_scrollbar.config(command=tree.xview)
    
    # Colocar la tabla en el grid (se expandirá dinámicamente)
    tree.grid(row=0, column=0, sticky="nsew")
    
    # Configurar columnas
    tree.heading("codigo", text="Código")
    tree.heading("nombre", text="Nombre")
    tree.heading("categoria", text="Categoría")
    tree.heading("cantidad", text="Cantidad")
    tree.heading("precio_unitario", text="Precio Unit.")
    tree.heading("ganancia_unit", text="Ganancia Unit.")
    tree.heading("valor_venta", text="Valor de Venta")
    tree.heading("valor_base", text="Valor Base")
    tree.heading("valor_ganancia", text="Valor Ganancia")
    tree.heading("subtotal", text="Subtotal")
    
    # Anchos de columnas
    tree.column("codigo", width=100, anchor=tk.CENTER)
    tree.column("nombre", width=150, anchor=tk.W)
    tree.column("categoria", width=120, anchor=tk.W)
    tree.column("cantidad", width=80, anchor=tk.CENTER)
    tree.column("precio_unitario", width=100, anchor=tk.E)
    tree.column("ganancia_unit", width=110, anchor=tk.E)
    tree.column("valor_venta", width=110, anchor=tk.E)
    tree.column("valor_base", width=100, anchor=tk.E)
    tree.column("valor_ganancia", width=120, anchor=tk.E)
    tree.column("subtotal", width=100, anchor=tk.E)
    
    return tree


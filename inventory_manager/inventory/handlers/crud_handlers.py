"""Handlers para operaciones CRUD de productos."""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Optional, Union

from ...services.inventory_service import InventoryService
from .form_handlers import get_form_data, clear_form


def agregar_producto(
    window: tk.Widget,
    entries: Dict[str, Union[tk.Entry, ttk.Combobox]],
    ganancia_entry: tk.Entry,
    tree: tk.Widget,
    codigo_lateral_entry: tk.Entry,
    service: InventoryService,
    on_refresh: callable
):
    """
    Agrega un nuevo producto al inventario.
    
    Args:
        window: Ventana padre para mensajes
        entries: Diccionario con los entries del formulario
        ganancia_entry: Entry de ganancia
        tree: Treeview para refrescar
        codigo_lateral_entry: Entry del código lateral
        service: Servicio de inventario
        on_refresh: Función callback para refrescar la vista
    """
    exito, resultado = get_form_data(entries, ganancia_entry, service)
    
    if not exito:
        messagebox.showerror("Error", resultado, parent=window)
        return
    
    datos = resultado
    
    # Agregar producto usando el servicio
    exito, mensaje = service.agregar_producto(
        codigo=datos["codigo"],
        nombre=datos["nombre"],
        categoria=datos["categoria"],
        cantidad=datos["cantidad"],
        precio_unitario=datos["precio_unitario"],
        ganancia=datos["ganancia"]
    )
    
    if exito:
        messagebox.showinfo("Éxito", mensaje, parent=window)
        clear_form(entries, ganancia_entry, codigo_lateral_entry, tree, service)
        on_refresh()
    else:
        messagebox.showerror("Error", mensaje, parent=window)


def actualizar_producto(
    window: tk.Widget,
    producto_seleccionado: Optional[str],
    entries: Dict[str, Union[tk.Entry, ttk.Combobox]],
    ganancia_entry: tk.Entry,
    tree: tk.Widget,
    codigo_lateral_entry: tk.Entry,
    service: InventoryService,
    on_refresh: callable
) -> Optional[str]:
    """
    Actualiza un producto existente.
    
    Args:
        window: Ventana padre para mensajes
        producto_seleccionado: Código del producto seleccionado
        entries: Diccionario con los entries del formulario
        ganancia_entry: Entry de ganancia
        tree: Treeview para refrescar
        codigo_lateral_entry: Entry del código lateral
        service: Servicio de inventario
        on_refresh: Función callback para refrescar la vista
        
    Returns:
        Optional[str]: None si se actualizó correctamente, o el código seleccionado si hubo error
    """
    if not producto_seleccionado:
        messagebox.showerror("Error", "Debe seleccionar un producto de la tabla para actualizar.", parent=window)
        return producto_seleccionado
    
    exito, resultado = get_form_data(entries, ganancia_entry, service)
    
    if not exito:
        messagebox.showerror("Error", resultado, parent=window)
        return producto_seleccionado
    
    datos = resultado
    codigo_original = producto_seleccionado
    codigo_nuevo = datos["codigo"]
    
    # Actualizar producto
    exito, mensaje = service.actualizar_producto(
        codigo_original=codigo_original,
        codigo=codigo_nuevo,
        nombre=datos["nombre"],
        categoria=datos["categoria"],
        cantidad=datos["cantidad"],
        precio_unitario=datos["precio_unitario"],
        ganancia=datos["ganancia"]
    )
    
    if exito:
        messagebox.showinfo("Éxito", mensaje, parent=window)
        clear_form(entries, ganancia_entry, codigo_lateral_entry, tree, service)
        on_refresh()
        return None
    else:
        messagebox.showerror("Error", mensaje, parent=window)
        return producto_seleccionado


def eliminar_producto(
    window: tk.Widget,
    producto_seleccionado: Optional[str],
    entries: Dict[str, Union[tk.Entry, ttk.Combobox]],
    ganancia_entry: tk.Entry,
    tree: tk.Widget,
    codigo_lateral_entry: tk.Entry,
    service: InventoryService,
    on_refresh: callable
) -> Optional[str]:
    """
    Elimina un producto del inventario.
    
    Args:
        window: Ventana padre para mensajes
        producto_seleccionado: Código del producto seleccionado
        entries: Diccionario con los entries del formulario
        ganancia_entry: Entry de ganancia
        tree: Treeview para refrescar
        codigo_lateral_entry: Entry del código lateral
        service: Servicio de inventario
        on_refresh: Función callback para refrescar la vista
        
    Returns:
        Optional[str]: None si se eliminó correctamente, o el código seleccionado si hubo error
    """
    if not producto_seleccionado:
        messagebox.showerror("Error", "Debe seleccionar un producto de la tabla para eliminar.", parent=window)
        return producto_seleccionado
    
    # Confirmar eliminación
    respuesta = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Está seguro de eliminar el producto '{producto_seleccionado}'?",
        parent=window
    )
    
    if not respuesta:
        return producto_seleccionado
    
    # Eliminar producto
    exito, mensaje = service.eliminar_producto(producto_seleccionado)
    
    if exito:
        messagebox.showinfo("Éxito", mensaje, parent=window)
        clear_form(entries, ganancia_entry, codigo_lateral_entry, tree, service)
        on_refresh()
        return None
    else:
        messagebox.showerror("Error", mensaje, parent=window)
        return producto_seleccionado


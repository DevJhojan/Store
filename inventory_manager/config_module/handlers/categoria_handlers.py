"""Handlers para gestión de categorías."""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, Optional, Callable

from ..services.categoria_service import CategoriaService
from ...utils.validators import validate_fields


def refresh_categoria_table(
    tree: ttk.Treeview,
    service: CategoriaService
):
    """
    Actualiza la tabla de categorías.
    
    Args:
        tree: Treeview a actualizar
        service: Servicio de categorías
    """
    # Limpiar tabla
    for item in tree.get_children():
        tree.delete(item)
    
    # Obtener todas las categorías
    categorias = service.obtener_todas_las_categorias()
    
    # Agregar categorías a la tabla
    for categoria in categorias:
        tree.insert(
            "",
            tk.END,
            values=(
                categoria.id,
                categoria.nombre,
                categoria.descripcion or ""
            )
        )


def on_categoria_selected(
    event,
    tree: ttk.Treeview,
    service: CategoriaService,
    form_widgets: Dict[str, tk.Widget],
    summary_labels: Optional[Dict[str, tk.Label]] = None
) -> Optional[int]:
    """
    Maneja la selección de una categoría en la tabla.
    
    Args:
        event: Evento de selección
        tree: Treeview
        service: Servicio de categorías
        form_widgets: Widgets del formulario
        
    Returns:
        Optional[int]: ID de la categoría seleccionada o None
    """
    selection = tree.selection()
    if not selection:
        return None
    
    item = tree.item(selection[0])
    valores = item['values']
    
    if len(valores) >= 2:
        categoria_id = valores[0]
        
        # Cargar datos de la categoría
        categoria = service.obtener_categoria_por_id(categoria_id)
        if categoria:
            form_widgets["nombre"].delete(0, tk.END)
            form_widgets["nombre"].insert(0, categoria.nombre)
            
            form_widgets["descripcion"].delete(0, tk.END)
            if categoria.descripcion:
                form_widgets["descripcion"].insert(0, categoria.descripcion)
            
            # Actualizar resumen
            if summary_labels:
                summary_labels["title"].config(text=f"Resumen de '{categoria.nombre}'")
                summary_labels["description"].config(
                    text=categoria.descripcion if categoria.descripcion else "Sin descripción"
                )
            
            return categoria_id
    
    return None


def agregar_categoria(
    window: tk.Widget,
    form_widgets: Dict[str, tk.Widget],
    service: CategoriaService,
    on_refresh: Callable,
    summary_labels: Optional[Dict[str, tk.Label]] = None
):
    """
    Agrega una nueva categoría.
    
    Args:
        window: Ventana padre para mensajes
        form_widgets: Widgets del formulario
        service: Servicio de categorías
        on_refresh: Función callback para refrescar la vista
    """
    nombre = form_widgets["nombre"].get().strip()
    descripcion = form_widgets["descripcion"].get().strip() or None
    
    if not nombre:
        messagebox.showerror("Error", "El nombre de la categoría es obligatorio.", parent=window)
        return
    
    exito, mensaje = service.agregar_categoria(nombre, descripcion)
    
    if exito:
        messagebox.showinfo("Éxito", mensaje, parent=window)
        limpiar_formulario_categoria(form_widgets, summary_labels=summary_labels)
        on_refresh()
    else:
        messagebox.showerror("Error", mensaje, parent=window)


def actualizar_categoria(
    window: tk.Widget,
    categoria_seleccionada_id: Optional[int],
    form_widgets: Dict[str, tk.Widget],
    service: CategoriaService,
    on_refresh: Callable,
    summary_labels: Optional[Dict[str, tk.Label]] = None
) -> Optional[int]:
    """
    Actualiza una categoría existente.
    
    Args:
        window: Ventana padre para mensajes
        categoria_seleccionada_id: ID de la categoría seleccionada
        form_widgets: Widgets del formulario
        service: Servicio de categorías
        on_refresh: Función callback para refrescar la vista
        
    Returns:
        Optional[int]: None si se actualizó correctamente, o el ID si hubo error
    """
    if not categoria_seleccionada_id:
        messagebox.showerror("Error", "Debe seleccionar una categoría de la tabla para actualizar.", parent=window)
        return categoria_seleccionada_id
    
    nombre = form_widgets["nombre"].get().strip()
    descripcion = form_widgets["descripcion"].get().strip() or None
    
    if not nombre:
        messagebox.showerror("Error", "El nombre de la categoría es obligatorio.", parent=window)
        return categoria_seleccionada_id
    
    exito, mensaje = service.actualizar_categoria(categoria_seleccionada_id, nombre, descripcion)
    
    if exito:
        messagebox.showinfo("Éxito", mensaje, parent=window)
        limpiar_formulario_categoria(form_widgets, summary_labels=summary_labels)
        on_refresh()
        return None
    else:
        messagebox.showerror("Error", mensaje, parent=window)
        return categoria_seleccionada_id


def eliminar_categoria(
    window: tk.Widget,
    categoria_seleccionada_id: Optional[int],
    form_widgets: Dict[str, tk.Widget],
    service: CategoriaService,
    on_refresh: Callable,
    summary_labels: Optional[Dict[str, tk.Label]] = None
) -> Optional[int]:
    """
    Elimina una categoría.
    
    Args:
        window: Ventana padre para mensajes
        categoria_seleccionada_id: ID de la categoría seleccionada
        form_widgets: Widgets del formulario
        service: Servicio de categorías
        on_refresh: Función callback para refrescar la vista
        
    Returns:
        Optional[int]: None si se eliminó correctamente, o el ID si hubo error
    """
    if not categoria_seleccionada_id:
        messagebox.showerror("Error", "Debe seleccionar una categoría de la tabla para eliminar.", parent=window)
        return categoria_seleccionada_id
    
    # Confirmar eliminación
    respuesta = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Está seguro de eliminar esta categoría?",
        parent=window
    )
    
    if not respuesta:
        return categoria_seleccionada_id
    
    exito, mensaje = service.eliminar_categoria(categoria_seleccionada_id)
    
    if exito:
        messagebox.showinfo("Éxito", mensaje, parent=window)
        limpiar_formulario_categoria(form_widgets, summary_labels=summary_labels)
        on_refresh()
        return None
    else:
        messagebox.showerror("Error", mensaje, parent=window)
        return categoria_seleccionada_id


def limpiar_formulario_categoria(
    form_widgets: Dict[str, tk.Widget], 
    tree: Optional[ttk.Treeview] = None,
    summary_labels: Optional[Dict[str, tk.Label]] = None
):
    """
    Limpia el formulario de categoría.
    
    Args:
        form_widgets: Widgets del formulario
        tree: Treeview opcional para deseleccionar items
        summary_labels: Labels del resumen opcional para limpiar
    """
    form_widgets["nombre"].delete(0, tk.END)
    form_widgets["descripcion"].delete(0, tk.END)
    
    if tree:
        for item in tree.selection():
            tree.selection_remove(item)
    
    if summary_labels:
        summary_labels["title"].config(text="Resumen de ''")
        summary_labels["description"].config(text="")


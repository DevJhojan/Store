"""Handlers para gestión de información de tienda."""
import tkinter as tk
from tkinter import messagebox
from typing import Dict

from ..services.tienda_service import TiendaService


def cargar_informacion_tienda(
    widgets: Dict[str, tk.Widget],
    service: TiendaService
):
    """
    Carga la información de la tienda en los widgets.
    
    Args:
        widgets: Widgets del formulario
        service: Servicio de tienda
    """
    tienda_info = service.obtener_informacion_tienda()
    
    if tienda_info:
        widgets["nombre"].delete(0, tk.END)
        widgets["nombre"].insert(0, tienda_info.nombre)
        
        widgets["descripcion"].delete("1.0", tk.END)
        if tienda_info.descripcion:
            widgets["descripcion"].insert("1.0", tienda_info.descripcion)
    else:
        # Limpiar si no hay información
        widgets["nombre"].delete(0, tk.END)
        widgets["descripcion"].delete("1.0", tk.END)


def guardar_informacion_tienda(
    window: tk.Widget,
    widgets: Dict[str, tk.Widget],
    service: TiendaService
):
    """
    Guarda la información de la tienda.
    
    Args:
        window: Ventana padre para mensajes
        widgets: Widgets del formulario
        service: Servicio de tienda
    """
    nombre = widgets["nombre"].get().strip()
    descripcion = widgets["descripcion"].get("1.0", tk.END).strip() or None
    
    if not nombre:
        messagebox.showerror("Error", "El nombre de la tienda es obligatorio.", parent=window)
        return
    
    exito, mensaje = service.guardar_informacion_tienda(nombre, descripcion)
    
    if exito:
        messagebox.showinfo("Éxito", mensaje, parent=window)
    else:
        messagebox.showerror("Error", mensaje, parent=window)


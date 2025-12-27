"""Handlers para eventos del formulario."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Union

from ...services.inventory_service import InventoryService
from ...utils.validators import validate_fields, parse_numeric_field
from ..utils.code_generator import generar_codigo_autoincremental
from ..utils.calculations import calcular_valores_producto


def load_product_to_form(
    producto,
    entries: Dict[str, Union[tk.Entry, ttk.Combobox]],
    ganancia_entry: tk.Entry,
    codigo_lateral_entry: tk.Entry
):
    """
    Carga los datos de un producto en el formulario.
    
    Args:
        producto: Producto a cargar
        entries: Diccionario con los entries del formulario
        ganancia_entry: Entry de ganancia
        codigo_lateral_entry: Entry del código lateral
    """
    entries["codigo"].config(state="normal")
    entries["codigo"].delete(0, tk.END)
    entries["codigo"].insert(0, producto.codigo)
    entries["codigo"].config(state="readonly")
    
    codigo_lateral_entry.config(state="normal")
    codigo_lateral_entry.delete(0, tk.END)
    codigo_lateral_entry.insert(0, producto.codigo)
    codigo_lateral_entry.config(state="readonly")
    
    entries["nombre"].delete(0, tk.END)
    entries["nombre"].insert(0, producto.nombre)
    
    # Manejar categoría (puede ser Entry o Combobox)
    if hasattr(entries["categoria"], 'set'):
        # Es un Combobox
        entries["categoria"].set(producto.categoria)
    else:
        # Es un Entry
        entries["categoria"].delete(0, tk.END)
        entries["categoria"].insert(0, producto.categoria)
    
    entries["cantidad"].delete(0, tk.END)
    entries["cantidad"].insert(0, str(producto.cantidad))
    
    entries["precio_unitario"].delete(0, tk.END)
    entries["precio_unitario"].insert(0, str(producto.precio_unitario))
    
    ganancia_entry.delete(0, tk.END)
    ganancia_entry.insert(0, f"{producto.ganancia:.2f}")


def clear_form(
    entries: Dict[str, Union[tk.Entry, ttk.Combobox]],
    ganancia_entry: tk.Entry,
    codigo_lateral_entry: tk.Entry,
    tree: tk.Widget,
    service: InventoryService
):
    """
    Limpia todos los campos del formulario.
    
    Args:
        entries: Diccionario con los entries del formulario
        ganancia_entry: Entry de ganancia
        codigo_lateral_entry: Entry del código lateral
        tree: Treeview para deseleccionar items
        service: Servicio de inventario para generar código
    """
    # Generar nuevo código
    productos = service.obtener_todos_los_productos()
    nuevo_codigo = generar_codigo_autoincremental(productos)
    
    # Limpiar campos
    entries["codigo"].config(state="normal")
    entries["codigo"].delete(0, tk.END)
    entries["codigo"].insert(0, nuevo_codigo)
    entries["codigo"].config(state="readonly")
    
    codigo_lateral_entry.config(state="normal")
    codigo_lateral_entry.delete(0, tk.END)
    codigo_lateral_entry.insert(0, nuevo_codigo)
    codigo_lateral_entry.config(state="readonly")
    
    entries["nombre"].delete(0, tk.END)
    
    # Manejar categoría (puede ser Entry o Combobox)
    if hasattr(entries["categoria"], 'set'):
        # Es un Combobox
        entries["categoria"].set("")
    else:
        # Es un Entry
        entries["categoria"].delete(0, tk.END)
    entries["cantidad"].delete(0, tk.END)
    entries["precio_unitario"].delete(0, tk.END)
    
    ganancia_entry.delete(0, tk.END)
    ganancia_entry.insert(0, "0")
    
    # Deseleccionar en tabla
    for item in tree.selection():
        tree.selection_remove(item)


def get_form_data(
    entries: Dict[str, Union[tk.Entry, ttk.Combobox]],
    ganancia_entry: tk.Entry,
    service: InventoryService
) -> tuple:
    """
    Obtiene y valida los datos del formulario.
    
    Args:
        entries: Diccionario con los entries del formulario
        ganancia_entry: Entry de ganancia
        service: Servicio de inventario para generar código si es necesario
        
    Returns:
        tuple: (exito, datos) donde datos es un dict con los datos o mensaje de error
    """
    # Validar campos requeridos
    campos_requeridos = {
        "nombre": "Nombre",
        "categoria": "Categoría",
        "cantidad": "Cantidad",
        "precio_unitario": "Precio unitario"
    }
    
    es_valido, key, nombre = validate_fields(
        {k: entries[k] for k in campos_requeridos.keys()},
        campos_requeridos
    )
    
    if not es_valido:
        return False, f"El campo '{nombre}' es obligatorio."
    
    # Parsear valores numéricos
    cantidad_ok, cantidad, error_cantidad = parse_numeric_field(
        entries["cantidad"].get(), int
    )
    if not cantidad_ok:
        return False, f"Cantidad: {error_cantidad}"
    
    precio_ok, precio, error_precio = parse_numeric_field(
        entries["precio_unitario"].get(), float
    )
    if not precio_ok:
        return False, f"Precio unitario: {error_precio}"
    
    # Parsear ganancia
    ganancia_ok, ganancia, error_ganancia = parse_numeric_field(
        ganancia_entry.get(), float
    )
    if not ganancia_ok:
        ganancia = 0.0
    
    # Obtener código (generar si no existe)
    codigo = entries["codigo"].get().strip()
    if not codigo:
        productos = service.obtener_todos_los_productos()
        codigo = generar_codigo_autoincremental(productos)
    
    datos = {
        "codigo": codigo,
        "nombre": entries["nombre"].get().strip(),
        "categoria": entries["categoria"].get().strip(),
        "cantidad": cantidad,
        "precio_unitario": precio,
        "ganancia": ganancia
    }
    
    return True, datos


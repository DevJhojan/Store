"""Handlers para eventos de la tabla."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from ...services.inventory_service import InventoryService
from ..utils.calculations import calcular_valores_producto
from .form_handlers import load_product_to_form


def refresh_table(
    tree: ttk.Treeview,
    service: InventoryService,
    summary_labels: Dict[str, tk.Label]
):
    """
    Actualiza la tabla y el resumen con los productos actuales.
    
    Args:
        tree: Treeview a actualizar
        service: Servicio de inventario
        summary_labels: Labels del resumen para actualizar
    """
    # Limpiar tabla
    for item in tree.get_children():
        tree.delete(item)
    
    # Obtener todos los productos
    productos = service.obtener_todos_los_productos()
    
    # Variables para resumen
    total_productos = len(productos)
    valor_total_base = 0.0
    valor_total_ganancia = 0.0
    valor_total_subtotal = 0.0
    
    # Agregar productos a la tabla
    for producto in productos:
        # Usar ganancia del producto
        ganancia = producto.ganancia
        
        # Calcular valores
        valor_base, valor_ganancia, subtotal = calcular_valores_producto(
            producto.cantidad,
            producto.precio_unitario,
            ganancia
        )
        
        # Calcular ganancia unitaria
        ganancia_unit = producto.precio_unitario * (ganancia / 100.0)
        
        # Asegurar que valor_venta esté calculado
        if producto.valor_venta == 0.0:
            producto.valor_venta = producto.calcular_valor_venta()
        
        # Agregar a tabla
        tree.insert(
            "",
            tk.END,
            values=(
                producto.codigo,
                producto.nombre,
                producto.categoria,
                producto.cantidad,
                f"${producto.precio_unitario:.2f}",
                f"${ganancia_unit:.2f}",
                f"${producto.valor_venta:.2f}",
                f"${valor_base:.2f}",
                f"${valor_ganancia:.2f}",
                f"${subtotal:.2f}"
            )
        )
        
        # Acumular para resumen
        valor_total_base += valor_base
        valor_total_ganancia += valor_ganancia
        valor_total_subtotal += subtotal
    
    # Actualizar resumen
    summary_labels["total_productos"].config(text=f"Total Productos: {total_productos}")
    summary_labels["valor_total_base"].config(text=f"Valor Total Base: ${valor_total_base:,.2f}")
    summary_labels["valor_total_ganancia"].config(text=f"Valor Total Ganancia: ${valor_total_ganancia:,.2f}")
    summary_labels["valor_total_subtotal"].config(text=f"TOTAL: ${valor_total_subtotal:,.2f}")


def on_producto_seleccionado(
    event,
    tree: ttk.Treeview,
    service: InventoryService,
    entries: Dict[str, tk.Entry],
    ganancia_entry: tk.Entry,
    codigo_lateral_entry: tk.Entry
) -> Optional[str]:
    """
    Maneja la selección de un producto en la tabla.
    
    Args:
        event: Evento de selección
        tree: Treeview
        service: Servicio de inventario
        entries: Diccionario con los entries del formulario
        ganancia_entry: Entry de ganancia
        codigo_lateral_entry: Entry del código lateral
        
    Returns:
        Optional[str]: Código del producto seleccionado o None
    """
    selection = tree.selection()
    if not selection:
        return None
    
    item = tree.item(selection[0])
    valores = item['values']
    
    if len(valores) >= 6:
        codigo = valores[0]
        
        # Cargar datos del producto
        producto = service.obtener_producto_por_codigo(codigo)
        if producto:
            load_product_to_form(producto, entries, ganancia_entry, codigo_lateral_entry)
            return codigo
    
    return None


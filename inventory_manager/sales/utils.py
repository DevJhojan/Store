"""Utilidades para cálculos de ventas."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.models import Venta


def calcular_totales_venta(
    venta: "Venta",
    impuesto_porcentaje_venta: float,
    descuento_fijo_venta: float,
    descuento_porcentaje_venta: float
) -> tuple:
    """
    Calcula los totales de una venta incluyendo impuestos y descuentos.
    
    Args:
        venta: Objeto Venta con sus items
        impuesto_porcentaje_venta: Porcentaje de impuesto a nivel de venta (0-1)
        descuento_fijo_venta: Descuento fijo a nivel de venta
        descuento_porcentaje_venta: Porcentaje de descuento a nivel de venta (0-1)
        
    Returns:
        tuple: (subtotal_items, descuento_total, impuesto_total, total_final)
    """
    # Calcular subtotal desde items
    subtotal_items = sum(item.calcular_subtotal() for item in venta.items)
    descuento_items = sum(item.calcular_descuento() for item in venta.items)
    
    # Aplicar descuentos a nivel de venta
    subtotal_con_descuento_items = subtotal_items - descuento_items
    
    # Descuento fijo
    descuento_fijo_aplicado = descuento_fijo_venta
    
    # Descuento porcentual sobre el subtotal con descuento de items
    descuento_porcentual_aplicado = subtotal_con_descuento_items * descuento_porcentaje_venta
    
    # Subtotal después de todos los descuentos
    subtotal_final = subtotal_con_descuento_items - descuento_fijo_aplicado - descuento_porcentual_aplicado
    if subtotal_final < 0:
        subtotal_final = 0.0
    
    # Calcular impuesto sobre el subtotal final
    impuesto_aplicado = subtotal_final * impuesto_porcentaje_venta
    impuesto_items = sum(item.calcular_impuesto() for item in venta.items)
    
    # Total final
    total_final = subtotal_final + impuesto_aplicado + impuesto_items
    
    # Calcular descuento total
    descuento_total = descuento_items + descuento_fijo_aplicado + descuento_porcentual_aplicado
    impuesto_total = impuesto_items + impuesto_aplicado
    
    return subtotal_items, descuento_total, impuesto_total, total_final


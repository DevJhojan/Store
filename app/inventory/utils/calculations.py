"""Utilidades para cálculos de valores de productos."""


def calcular_valores_producto(cantidad: int, precio_unitario: float, ganancia: float) -> tuple:
    """
    Calcula los valores financieros de un producto.
    
    Args:
        cantidad: Cantidad del producto
        precio_unitario: Precio unitario
        ganancia: Porcentaje de ganancia
        
    Returns:
        tuple: (valor_base, valor_ganancia, subtotal)
    """
    valor_base = cantidad * precio_unitario
    valor_ganancia = valor_base * (ganancia / 100.0)
    subtotal = valor_base + valor_ganancia
    return valor_base, valor_ganancia, subtotal


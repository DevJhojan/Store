"""Generador de códigos autoincrementales para productos."""
from typing import List

from ...domain.models import Producto


def generar_codigo_autoincremental(productos: List[Producto]) -> str:
    """
    Genera un código autoincremental para un nuevo producto.
    
    Args:
        productos: Lista de productos existentes
        
    Returns:
        str: Código generado (PROD001, PROD002, etc.)
    """
    if not productos:
        return "PROD001"
    
    # Buscar el mayor número de código existente
    max_num = 0
    for producto in productos:
        if producto.codigo.startswith("PROD"):
            try:
                num = int(producto.codigo[4:])
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
    
    # Generar nuevo código
    nuevo_num = max_num + 1
    return f"PROD{nuevo_num:03d}"


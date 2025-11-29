"""Sistema de Gestión de Inventarios - Paquete Python instalable.

Este paquete proporciona un sistema completo de gestión de inventarios
con interfaz gráfica usando tkinter y almacenamiento en SQLite.
"""

__version__ = "1.0.0"
__author__ = "Store Development Team"

from .domain import Producto
from .services import InventoryService
from .repository import ProductRepository
from .ui import InventoryManagerGUI

__all__ = [
    "Producto",
    "InventoryService",
    "ProductRepository",
    "InventoryManagerGUI",
]


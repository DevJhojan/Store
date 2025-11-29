"""Sistema de Gestión - Paquete Python instalable.

Este paquete proporciona un sistema completo de gestión con módulos
de Inventarios y Ventas, con interfaz gráfica usando tkinter y
almacenamiento en SQLite.
"""

__version__ = "2.0.0"
__author__ = "Store Development Team"

from .domain import Producto
from .services import InventoryService
from .repository import ProductRepository
from .main_window import MainWindow
from .sales.ui.views import SalesGUI

__all__ = [
    "Producto",
    "InventoryService",
    "ProductRepository",
    "MainWindow",
    "SalesGUI",
]


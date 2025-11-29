"""Modelos de dominio para el módulo de Ventas."""
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ItemVenta:
    """Modelo de un item de venta (producto vendido)."""
    
    codigo_producto: str
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    
    def calcular_subtotal(self) -> float:
        """Calcula el subtotal del item."""
        return self.cantidad * self.precio_unitario
    
    def validar(self) -> tuple[bool, str | None]:
        """Valida que el item tenga todos los campos requeridos."""
        if not self.codigo_producto or not self.codigo_producto.strip():
            return False, "El código del producto es obligatorio."
        
        if not self.nombre_producto or not self.nombre_producto.strip():
            return False, "El nombre del producto es obligatorio."
        
        if self.cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0."
        
        if self.precio_unitario <= 0:
            return False, "El precio unitario debe ser mayor a 0."
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convierte el item a un diccionario."""
        return {
            "codigo_producto": self.codigo_producto,
            "nombre_producto": self.nombre_producto,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario
        }


@dataclass
class Venta:
    """Modelo de una venta."""
    
    id: int = 0  # Se asigna automáticamente por la BD
    fecha: datetime = None
    items: List[ItemVenta] = None
    total: float = 0.0
    
    def __post_init__(self):
        """Inicializar valores por defecto."""
        if self.fecha is None:
            self.fecha = datetime.now()
        if self.items is None:
            self.items = []
        if self.total == 0.0 and self.items:
            self.calcular_total()
    
    def agregar_item(self, item: ItemVenta):
        """Agrega un item a la venta."""
        es_valido, mensaje_error = item.validar()
        if not es_valido:
            raise ValueError(mensaje_error)
        
        self.items.append(item)
        self.calcular_total()
    
    def remover_item(self, index: int):
        """Remueve un item de la venta por índice."""
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.calcular_total()
    
    def calcular_total(self) -> float:
        """Calcula el total de la venta."""
        self.total = sum(item.calcular_subtotal() for item in self.items)
        return self.total
    
    def validar(self) -> tuple[bool, str | None]:
        """Valida que la venta sea válida."""
        if not self.items:
            return False, "La venta debe tener al menos un producto."
        
        for i, item in enumerate(self.items):
            es_valido, mensaje_error = item.validar()
            if not es_valido:
                return False, f"Error en item {i+1}: {mensaje_error}"
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convierte la venta a un diccionario."""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "items": [item.to_dict() for item in self.items],
            "total": self.total
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Venta":
        """Crea una venta desde un diccionario."""
        from datetime import datetime
        
        items = [ItemVenta(**item) for item in data.get("items", [])]
        fecha_str = data.get("fecha")
        fecha = datetime.fromisoformat(fecha_str) if fecha_str else datetime.now()
        
        return cls(
            id=data.get("id", 0),
            fecha=fecha,
            items=items,
            total=data.get("total", 0.0)
        )


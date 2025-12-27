"""Modelos de dominio del sistema de inventario."""
from dataclasses import dataclass


@dataclass
class Producto:
    """Modelo de producto en el inventario."""
    
    codigo: str
    nombre: str
    categoria: str
    cantidad: int
    precio_unitario: float
    ganancia: float = 0.0  # Porcentaje de ganancia
    valor_venta: float = 0.0  # Precio unitario + ganancia unitaria
    
    def calcular_ganancia_unitaria(self) -> float:
        """Calcula la ganancia unitaria en valor monetario."""
        return self.precio_unitario * (self.ganancia / 100.0)
    
    def calcular_valor_venta(self) -> float:
        """Calcula el valor de venta (precio unitario + ganancia unitaria)."""
        ganancia_unit = self.calcular_ganancia_unitaria()
        return self.precio_unitario + ganancia_unit
    
    def calcular_subtotal(self) -> float:
        """Calcula el subtotal del producto (cantidad * precio_unitario)."""
        return self.cantidad * self.precio_unitario
    
    def validar(self) -> tuple[bool, str | None]:
        """
        Valida que el producto tenga todos los campos requeridos.
        
        Returns:
            tuple[bool, str | None]: (es_valido, mensaje_error)
        """
        if not self.codigo or not self.codigo.strip():
            return False, "El código es obligatorio."
        
        if not self.nombre or not self.nombre.strip():
            return False, "El nombre es obligatorio."
        
        if not self.categoria or not self.categoria.strip():
            return False, "La categoría es obligatoria."
        
        if self.cantidad < 0:
            return False, "La cantidad debe ser mayor o igual a 0."
        
        if self.precio_unitario < 0:
            return False, "El precio unitario debe ser mayor o igual a 0."
        
        if self.ganancia < 0:
            return False, "La ganancia debe ser mayor o igual a 0."
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convierte el producto a un diccionario."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "ganancia": self.ganancia,
            "valor_venta": self.valor_venta
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        """Crea un producto desde un diccionario."""
        producto = cls(
            codigo=data["codigo"],
            nombre=data["nombre"],
            categoria=data["categoria"],
            cantidad=data["cantidad"],
            precio_unitario=data["precio_unitario"],
            ganancia=data.get("ganancia", 0.0),
            valor_venta=data.get("valor_venta", 0.0)
        )
        # Recalcular valor_venta si no está o es 0
        if producto.valor_venta == 0.0:
            producto.valor_venta = producto.calcular_valor_venta()
        return producto
    
    @classmethod
    def from_tuple(cls, data: tuple) -> "Producto":
        """Crea un producto desde una tupla de la base de datos."""
        # Manejar compatibilidad con bases de datos antiguas
        ganancia = data[5] if len(data) > 5 else 0.0
        valor_venta = data[6] if len(data) > 6 else 0.0
        
        producto = cls(
            codigo=data[0],
            nombre=data[1],
            categoria=data[2],
            cantidad=data[3],
            precio_unitario=data[4],
            ganancia=ganancia,
            valor_venta=valor_venta
        )
        
        # Recalcular valor_venta si no está o es 0 (para productos antiguos)
        if producto.valor_venta == 0.0:
            producto.valor_venta = producto.calcular_valor_venta()
        
        return producto


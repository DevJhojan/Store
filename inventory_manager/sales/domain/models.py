"""Modelos de dominio para el módulo de Ventas."""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional
from enum import Enum


class MetodoPago(Enum):
    """Métodos de pago disponibles."""
    EFECTIVO = "Efectivo"
    TARJETA = "Tarjeta"
    TRANSFERENCIA = "Transferencia"
    CHEQUE = "Cheque"


@dataclass
class ItemVenta:
    """Modelo de un item de venta (producto vendido)."""
    
    codigo_producto: str
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    descuento: float = 0.0  # Porcentaje de descuento
    impuesto: float = 0.0  # Porcentaje de impuesto
    
    def calcular_subtotal(self) -> float:
        """Calcula el subtotal del item antes de descuentos e impuestos."""
        return self.cantidad * self.precio_unitario
    
    def calcular_descuento(self) -> float:
        """Calcula el monto del descuento."""
        subtotal = self.calcular_subtotal()
        return subtotal * (self.descuento / 100.0)
    
    def calcular_subtotal_con_descuento(self) -> float:
        """Calcula el subtotal después del descuento."""
        return self.calcular_subtotal() - self.calcular_descuento()
    
    def calcular_impuesto(self) -> float:
        """Calcula el monto del impuesto."""
        subtotal_con_descuento = self.calcular_subtotal_con_descuento()
        return subtotal_con_descuento * (self.impuesto / 100.0)
    
    def calcular_total(self) -> float:
        """Calcula el total del item (con descuento e impuesto)."""
        return self.calcular_subtotal_con_descuento() + self.calcular_impuesto()
    
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
            "precio_unitario": self.precio_unitario,
            "descuento": self.descuento,
            "impuesto": self.impuesto
        }


@dataclass
class Cliente:
    """Modelo de cliente."""
    
    id: int = 0
    nombre: str = ""
    documento: str = ""  # DNI, RUC, etc.
    telefono: str = ""
    email: str = ""
    direccion: str = ""
    fecha_registro: datetime = None
    
    def __post_init__(self):
        """Inicializar valores por defecto."""
        if self.fecha_registro is None:
            self.fecha_registro = datetime.now()
    
    def validar(self) -> tuple[bool, str | None]:
        """Valida que el cliente tenga datos mínimos."""
        if not self.nombre or not self.nombre.strip():
            return False, "El nombre del cliente es obligatorio."
        return True, None
    
    def to_dict(self) -> dict:
        """Convierte el cliente a un diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "documento": self.documento,
            "telefono": self.telefono,
            "email": self.email,
            "direccion": self.direccion,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None
        }


@dataclass
class Venta:
    """Modelo de una venta completa con facturación."""
    
    id: int = 0  # Se asigna automáticamente por la BD
    numero_factura: str = ""  # Número de factura incremental
    fecha: datetime = None
    items: List[ItemVenta] = None
    cliente_id: Optional[int] = None  # ID del cliente (opcional)
    subtotal: float = 0.0
    descuento_total: float = 0.0
    impuesto_total: float = 0.0
    total: float = 0.0
    metodo_pago: MetodoPago = MetodoPago.EFECTIVO
    observaciones: str = ""
    
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
        """Calcula el total de la venta con descuentos e impuestos."""
        self.subtotal = sum(item.calcular_subtotal() for item in self.items)
        self.descuento_total = sum(item.calcular_descuento() for item in self.items)
        subtotal_con_descuento = self.subtotal - self.descuento_total
        self.impuesto_total = sum(item.calcular_impuesto() for item in self.items)
        self.total = subtotal_con_descuento + self.impuesto_total
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
            "numero_factura": self.numero_factura,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "items": [item.to_dict() for item in self.items],
            "cliente_id": self.cliente_id,
            "subtotal": self.subtotal,
            "descuento_total": self.descuento_total,
            "impuesto_total": self.impuesto_total,
            "total": self.total,
            "metodo_pago": self.metodo_pago.value if isinstance(self.metodo_pago, MetodoPago) else self.metodo_pago,
            "observaciones": self.observaciones
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Venta":
        """Crea una venta desde un diccionario."""
        from datetime import datetime
        
        items = [ItemVenta(**item) for item in data.get("items", [])]
        fecha_str = data.get("fecha")
        fecha = datetime.fromisoformat(fecha_str) if fecha_str else datetime.now()
        
        metodo_pago_str = data.get("metodo_pago", "Efectivo")
        metodo_pago = MetodoPago(metodo_pago_str) if isinstance(metodo_pago_str, str) else metodo_pago_str
        
        return cls(
            id=data.get("id", 0),
            numero_factura=data.get("numero_factura", ""),
            fecha=fecha,
            items=items,
            cliente_id=data.get("cliente_id"),
            subtotal=data.get("subtotal", 0.0),
            descuento_total=data.get("descuento_total", 0.0),
            impuesto_total=data.get("impuesto_total", 0.0),
            total=data.get("total", 0.0),
            metodo_pago=metodo_pago,
            observaciones=data.get("observaciones", "")
        )


@dataclass
class Devolucion:
    """Modelo de devolución de productos."""
    
    id: int = 0
    venta_id: int = 0
    numero_factura: str = ""
    fecha: datetime = None
    items_devolucion: List[ItemVenta] = None  # Items devueltos
    motivo: str = ""
    generar_nota_credito: bool = False
    total_devolucion: float = 0.0
    
    def __post_init__(self):
        """Inicializar valores por defecto."""
        if self.fecha is None:
            self.fecha = datetime.now()
        if self.items_devolucion is None:
            self.items_devolucion = []
    
    def calcular_total(self) -> float:
        """Calcula el total de la devolución."""
        self.total_devolucion = sum(item.calcular_total() for item in self.items_devolucion)
        return self.total_devolucion
    
    def validar(self) -> tuple[bool, str | None]:
        """Valida que la devolución sea válida."""
        if not self.items_devolucion:
            return False, "La devolución debe tener al menos un producto."
        
        if not self.motivo or not self.motivo.strip():
            return False, "El motivo de la devolución es obligatorio."
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convierte la devolución a un diccionario."""
        return {
            "id": self.id,
            "venta_id": self.venta_id,
            "numero_factura": self.numero_factura,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "items_devolucion": [item.to_dict() for item in self.items_devolucion],
            "motivo": self.motivo,
            "generar_nota_credito": self.generar_nota_credito,
            "total_devolucion": self.total_devolucion
        }


@dataclass
class Gasto:
    """Modelo de gasto operativo."""
    
    id: int = 0
    fecha: datetime = None
    categoria: str = ""  # Agua, Servicios, Compras, Mantenimiento, etc.
    descripcion: str = ""
    monto: float = 0.0
    metodo_pago: MetodoPago = MetodoPago.EFECTIVO
    observaciones: str = ""
    
    def __post_init__(self):
        """Inicializar valores por defecto."""
        if self.fecha is None:
            self.fecha = datetime.now()
    
    def validar(self) -> tuple[bool, str | None]:
        """Valida que el gasto sea válido."""
        if not self.categoria or not self.categoria.strip():
            return False, "La categoría del gasto es obligatoria."
        
        if not self.descripcion or not self.descripcion.strip():
            return False, "La descripción del gasto es obligatoria."
        
        if self.monto <= 0:
            return False, "El monto del gasto debe ser mayor a 0."
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convierte el gasto a un diccionario."""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "monto": self.monto,
            "metodo_pago": self.metodo_pago.value if isinstance(self.metodo_pago, MetodoPago) else self.metodo_pago,
            "observaciones": self.observaciones
        }


@dataclass
class CierreCaja:
    """Modelo de cierre de caja diario."""
    
    id: int = 0
    fecha: date = None
    hora_cierre: datetime = None
    
    # Resumen financiero
    ventas_efectivo: float = 0.0
    ventas_tarjeta: float = 0.0
    ventas_transferencia: float = 0.0
    ventas_cheque: float = 0.0
    ventas_totales: float = 0.0
    
    impuestos_cobrados: float = 0.0
    gastos_totales: float = 0.0
    utilidad_neta: float = 0.0
    
    observaciones: str = ""
    
    def __post_init__(self):
        """Inicializar valores por defecto."""
        if self.fecha is None:
            self.fecha = date.today()
        if self.hora_cierre is None:
            self.hora_cierre = datetime.now()
    
    def calcular_ventas_totales(self) -> float:
        """Calcula el total de ventas."""
        self.ventas_totales = (
            self.ventas_efectivo +
            self.ventas_tarjeta +
            self.ventas_transferencia +
            self.ventas_cheque
        )
        return self.ventas_totales
    
    def calcular_utilidad_neta(self) -> float:
        """Calcula la utilidad neta."""
        self.calcular_ventas_totales()
        self.utilidad_neta = self.ventas_totales - self.impuestos_cobrados - self.gastos_totales
        return self.utilidad_neta
    
    def to_dict(self) -> dict:
        """Convierte el cierre de caja a un diccionario."""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "hora_cierre": self.hora_cierre.isoformat() if self.hora_cierre else None,
            "ventas_efectivo": self.ventas_efectivo,
            "ventas_tarjeta": self.ventas_tarjeta,
            "ventas_transferencia": self.ventas_transferencia,
            "ventas_cheque": self.ventas_cheque,
            "ventas_totales": self.ventas_totales,
            "impuestos_cobrados": self.impuestos_cobrados,
            "gastos_totales": self.gastos_totales,
            "utilidad_neta": self.utilidad_neta,
            "observaciones": self.observaciones
        }


@dataclass
class ConfiguracionImpuestos:
    """Modelo de configuración de impuestos."""
    
    id: int = 0
    nombre: str = ""  # IVA, ISV, etc.
    porcentaje: float = 0.0  # Porcentaje del impuesto
    activo: bool = True
    es_global: bool = True  # Si es global, se aplica a todos los productos por defecto
    
    def validar(self) -> tuple[bool, str | None]:
        """Valida que la configuración sea válida."""
        if not self.nombre or not self.nombre.strip():
            return False, "El nombre del impuesto es obligatorio."
        
        if self.porcentaje < 0:
            return False, "El porcentaje del impuesto no puede ser negativo."
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convierte la configuración a un diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "porcentaje": self.porcentaje,
            "activo": self.activo,
            "es_global": self.es_global
        }


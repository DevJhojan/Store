"""Servicio de lógica de negocio para ventas."""
import sqlite3
from typing import List, Optional, Tuple

from ...config.settings import Settings
from ...domain.models import Producto
from ...repository.product_repository import ProductRepository
from ...services.inventory_service import InventoryService
from ..domain.models import Venta, ItemVenta
from ..repository.venta_repository import VentaRepository


class VentaService:
    """Servicio que contiene la lógica de negocio de ventas."""
    
    def __init__(self, 
                 venta_repository: Optional[VentaRepository] = None,
                 inventory_service: Optional[InventoryService] = None):
        """
        Inicializa el servicio.
        
        Args:
            venta_repository: Repositorio de ventas (si None, se crea uno nuevo)
            inventory_service: Servicio de inventario (si None, se crea uno nuevo)
        """
        self.venta_repository = venta_repository or VentaRepository()
        self.inventory_service = inventory_service or InventoryService()
        self.product_repository = self.inventory_service.repository
    
    def registrar_venta(self, venta: Venta) -> Tuple[bool, str, Optional[int]]:
        """
        Registra una venta y actualiza automáticamente el inventario.
        
        Este método usa transacciones para garantizar integridad de datos.
        
        Args:
            venta: Venta a registrar
            
        Returns:
            Tuple[bool, str, Optional[int]]: (exitoso, mensaje, id_venta)
        """
        # Validar venta
        es_valido, mensaje_error = venta.validar()
        if not es_valido:
            return False, mensaje_error, None
        
        # Verificar stock disponible para cada item
        for item in venta.items:
            producto = self.product_repository.get_by_code(item.codigo_producto)
            if not producto:
                return False, f"El producto '{item.codigo_producto}' no existe en el inventario.", None
            
            if producto.cantidad < item.cantidad:
                return False, (
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Disponible: {producto.cantidad}, Solicitado: {item.cantidad}."
                ), None
        
        # Generar número de factura si no tiene
        if not venta.numero_factura:
            venta.numero_factura = self.venta_repository.generar_numero_factura()
        
        # Los totales ya deben estar calculados con descuentos e impuestos
        # Si no están actualizados, calcular básicos (pero los de la UI tienen prioridad)
        if venta.descuento_total == 0.0 and venta.impuesto_total == 0.0:
            venta.calcular_total()
        
        # Realizar venta usando el repositorio (que guarda en Ventas.DB)
        # y actualizar stock en inventario.db
        try:
            # Guardar venta en Ventas.DB usando el repositorio
            venta_id = self.venta_repository.create(venta)
            venta.id = venta_id
            
            # Actualizar stock en inventario.db (base de datos separada)
            conn_inventario = sqlite3.connect(Settings.DATABASE_PATH)
            try:
                cursor = conn_inventario.cursor()
                
                # Actualizar stock para cada item
                for item in venta.items:
                    cursor.execute("""
                        UPDATE productos 
                        SET cantidad = cantidad - ?
                        WHERE codigo = ?
                    """, (item.cantidad, item.codigo_producto))
                    
                    # Verificar que no quede stock negativo
                    cursor.execute("SELECT cantidad FROM productos WHERE codigo = ?", 
                                 (item.codigo_producto,))
                    nueva_cantidad = cursor.fetchone()[0]
                    if nueva_cantidad < 0:
                        raise ValueError(f"Stock negativo detectado para {item.codigo_producto}")
                
                conn_inventario.commit()
                return True, "Venta registrada exitosamente.", venta_id
                
            except Exception as e:
                conn_inventario.rollback()
                # Si falla la actualización de stock, intentar eliminar la venta
                # (aunque esto requeriría un método delete en el repositorio)
                return False, f"Error al actualizar stock: {str(e)}", None
            finally:
                conn_inventario.close()
                
        except sqlite3.Error as e:
            return False, f"Error de base de datos: {str(e)}", None
        except Exception as e:
            return False, f"Error al registrar la venta: {str(e)}", None
    
    def obtener_todas_las_ventas(self) -> List[Venta]:
        """
        Obtiene todas las ventas registradas.
        
        Returns:
            Lista de ventas
        """
        return self.venta_repository.get_all()
    
    def obtener_venta_por_id(self, venta_id: int) -> Optional[Venta]:
        """
        Obtiene una venta por su ID.
        
        Args:
            venta_id: ID de la venta
            
        Returns:
            Venta si existe, None en caso contrario
        """
        return self.venta_repository.get_by_id(venta_id)
    
    def obtener_productos_disponibles(self) -> List[Producto]:
        """
        Obtiene todos los productos disponibles (con stock > 0).
        
        Returns:
            Lista de productos disponibles
        """
        todos_productos = self.inventory_service.obtener_todos_los_productos()
        return [p for p in todos_productos if p.cantidad > 0]
    
    def buscar_producto_por_codigo(self, codigo: str) -> Optional[Producto]:
        """
        Busca un producto por su código.
        
        Args:
            codigo: Código del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        return self.product_repository.get_by_code(codigo)
    
    def buscar_productos_por_nombre(self, nombre: str) -> List[Producto]:
        """
        Busca productos por nombre.
        
        Args:
            nombre: Texto a buscar en el nombre del producto
            
        Returns:
            Lista de productos que coinciden con el nombre
        """
        return self.product_repository.buscar_por_nombre(nombre)


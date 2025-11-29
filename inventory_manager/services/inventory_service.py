"""Servicio de lógica de negocio para inventarios."""
from typing import List, Optional, Tuple

from ..domain.models import Producto
from ..repository.product_repository import ProductRepository


class InventoryService:
    """Servicio que contiene la lógica de negocio del inventario."""
    
    def __init__(self, repository: Optional[ProductRepository] = None):
        """
        Inicializa el servicio.
        
        Args:
            repository: Repositorio de productos (si None, se crea uno nuevo)
        """
        self.repository = repository or ProductRepository()
    
    def agregar_producto(self, codigo: str, nombre: str, categoria: str, 
                        cantidad: int, precio_unitario: float) -> Tuple[bool, str]:
        """
        Agrega un nuevo producto al inventario.
        
        Args:
            codigo: Código del producto
            nombre: Nombre del producto
            categoria: Categoría del producto
            cantidad: Cantidad disponible
            precio_unitario: Precio unitario
            
        Returns:
            Tuple[bool, str]: (exitoso, mensaje)
        """
        # Crear producto
        producto = Producto(
            codigo=codigo.strip(),
            nombre=nombre.strip(),
            categoria=categoria.strip(),
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        
        # Validar
        es_valido, mensaje_error = producto.validar()
        if not es_valido:
            return False, mensaje_error
        
        # Verificar si ya existe
        if self.repository.exists(producto.codigo):
            return False, "Ya existe un producto con ese código."
        
        # Crear en repositorio
        if self.repository.create(producto):
            return True, "Producto agregado correctamente."
        else:
            return False, "Error al agregar el producto."
    
    def actualizar_producto(self, codigo_original: str, codigo: str, nombre: str, 
                           categoria: str, cantidad: int, precio_unitario: float) -> Tuple[bool, str]:
        """
        Actualiza un producto existente.
        
        Args:
            codigo_original: Código original del producto
            codigo: Nuevo código (puede ser el mismo)
            nombre: Nuevo nombre
            categoria: Nueva categoría
            cantidad: Nueva cantidad
            precio_unitario: Nuevo precio unitario
            
        Returns:
            Tuple[bool, str]: (exitoso, mensaje)
        """
        # Crear producto con datos actualizados
        producto = Producto(
            codigo=codigo.strip(),
            nombre=nombre.strip(),
            categoria=categoria.strip(),
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        
        # Validar
        es_valido, mensaje_error = producto.validar()
        if not es_valido:
            return False, mensaje_error
        
        # Si el código cambió, verificar que no exista
        if codigo.strip() != codigo_original.strip():
            if self.repository.exists(producto.codigo):
                return False, "Ya existe un producto con ese código."
        
        # Actualizar
        if self.repository.update(codigo_original, producto):
            return True, "Producto actualizado correctamente."
        else:
            return False, "Error al actualizar el producto. Verifique que el producto exista."
    
    def eliminar_producto(self, codigo: str) -> Tuple[bool, str]:
        """
        Elimina un producto del inventario.
        
        Args:
            codigo: Código del producto a eliminar
            
        Returns:
            Tuple[bool, str]: (exitoso, mensaje)
        """
        if self.repository.delete(codigo):
            return True, "Producto eliminado correctamente."
        else:
            return False, "Error al eliminar el producto."
    
    def obtener_todos_los_productos(self) -> List[Producto]:
        """
        Obtiene todos los productos del inventario.
        
        Returns:
            Lista de productos
        """
        return self.repository.get_all()
    
    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Producto]:
        """
        Obtiene un producto por su código.
        
        Args:
            codigo: Código del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        return self.repository.get_by_code(codigo)
    
    def calcular_valor_total(self) -> float:
        """
        Calcula el valor total del inventario.
        
        Returns:
            float: Valor total del inventario
        """
        return self.repository.calculate_total_value()


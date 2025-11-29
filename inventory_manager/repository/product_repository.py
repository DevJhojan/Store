"""Repositorio para acceso a datos de productos."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager

from ..domain.models import Producto


class ProductRepository:
    """Repositorio para gestionar productos en la base de datos."""
    
    def __init__(self, db_path: str = "inventario.db"):
        """
        Inicializa el repositorio.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    codigo TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL
                )
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para obtener conexiones a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def create(self, product: Producto) -> bool:
        """
        Crea un nuevo producto en la base de datos.
        
        Args:
            product: Producto a crear
            
        Returns:
            bool: True si se creó exitosamente, False si ya existe
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO productos VALUES (?, ?, ?, ?, ?)",
                    (product.codigo, product.nombre, product.categoria, 
                     product.cantidad, product.precio_unitario)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_by_code(self, codigo: str) -> Optional[Producto]:
        """
        Obtiene un producto por su código.
        
        Args:
            codigo: Código del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
            row = cursor.fetchone()
            if row:
                return Producto.from_tuple(row)
            return None
    
    def get_all(self) -> List[Producto]:
        """
        Obtiene todos los productos.
        
        Returns:
            Lista de productos
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos")
            rows = cursor.fetchall()
            return [Producto.from_tuple(row) for row in rows]
    
    def update(self, codigo_original: str, product: Producto) -> bool:
        """
        Actualiza un producto existente.
        
        Args:
            codigo_original: Código original del producto a actualizar
            product: Datos actualizados del producto
            
        Returns:
            bool: True si se actualizó exitosamente, False si no existe
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE productos 
                    SET codigo = ?, nombre = ?, categoria = ?, cantidad = ?, precio_unitario = ?
                    WHERE codigo = ?
                """, (product.codigo, product.nombre, product.categoria, 
                      product.cantidad, product.precio_unitario, codigo_original))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
    
    def delete(self, codigo: str) -> bool:
        """
        Elimina un producto por su código.
        
        Args:
            codigo: Código del producto a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existe
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
            conn.commit()
            return cursor.rowcount > 0
    
    def exists(self, codigo: str) -> bool:
        """
        Verifica si existe un producto con el código dado.
        
        Args:
            codigo: Código a verificar
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        return self.get_by_code(codigo) is not None
    
    def calculate_total_value(self) -> float:
        """
        Calcula el valor total del inventario.
        
        Returns:
            float: Valor total (suma de cantidad * precio_unitario de todos los productos)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(cantidad * precio_unitario) FROM productos")
            result = cursor.fetchone()[0]
            return result if result else 0.0


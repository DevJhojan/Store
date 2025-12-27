"""Repositorio para acceso a datos de categorías."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager

from ..domain.models import Categoria


class CategoriaRepository:
    """Repositorio para gestionar categorías en la base de datos."""
    
    def __init__(self, db_path: str = "inventario.db"):
        """
        Inicializa el repositorio.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self._init_database()
        self._init_default_categorias()
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT
                )
            """)
            conn.commit()
    
    def _init_default_categorias(self):
        """Inicializa categorías por defecto si la tabla está vacía."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM categorias")
            count = cursor.fetchone()[0]
            
            if count == 0:
                categorias_default = [
                    ("Electrónica", "Productos electrónicos"),
                    ("Ropa", "Ropa y accesorios"),
                    ("Alimentos", "Productos alimenticios"),
                    ("Hogar", "Artículos para el hogar"),
                    ("Deportes", "Artículos deportivos"),
                    ("Libros", "Libros y material educativo"),
                    ("Juguetes", "Juguetes y juegos"),
                    ("Belleza", "Productos de belleza y cuidado personal"),
                    ("Automotriz", "Accesorios y repuestos automotrices"),
                    ("Oficina", "Artículos de oficina y papelería")
                ]
                
                for nombre, descripcion in categorias_default:
                    cursor.execute(
                        "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)",
                        (nombre, descripcion)
                    )
                conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para obtener conexiones a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def create(self, categoria: Categoria) -> bool:
        """
        Crea una nueva categoría en la base de datos.
        
        Args:
            categoria: Categoría a crear
            
        Returns:
            bool: True si se creó exitosamente, False si ya existe
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)",
                    (categoria.nombre.strip(), categoria.descripcion)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_all(self) -> List[Categoria]:
        """
        Obtiene todas las categorías.
        
        Returns:
            List[Categoria]: Lista de todas las categorías ordenadas por nombre
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
            rows = cursor.fetchall()
            return [Categoria.from_tuple(row) for row in rows]
    
    def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        """
        Obtiene una categoría por su ID.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            Optional[Categoria]: La categoría si existe, None si no
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nombre, descripcion FROM categorias WHERE id = ?",
                (categoria_id,)
            )
            row = cursor.fetchone()
            return Categoria.from_tuple(row) if row else None
    
    def get_by_nombre(self, nombre: str) -> Optional[Categoria]:
        """
        Obtiene una categoría por su nombre.
        
        Args:
            nombre: Nombre de la categoría
            
        Returns:
            Optional[Categoria]: La categoría si existe, None si no
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nombre, descripcion FROM categorias WHERE nombre = ?",
                (nombre.strip(),)
            )
            row = cursor.fetchone()
            return Categoria.from_tuple(row) if row else None
    
    def update(self, categoria: Categoria) -> bool:
        """
        Actualiza una categoría existente.
        
        Args:
            categoria: Categoría con los datos actualizados
            
        Returns:
            bool: True si se actualizó exitosamente, False si no existe
        """
        if not categoria.id:
            return False
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categorias SET nombre = ?, descripcion = ? WHERE id = ?",
                (categoria.nombre.strip(), categoria.descripcion, categoria.id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete(self, categoria_id: int) -> bool:
        """
        Elimina una categoría.
        
        Args:
            categoria_id: ID de la categoría a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existe
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def existe_categoria(self, nombre: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si existe una categoría con el nombre dado.
        
        Args:
            nombre: Nombre de la categoría a verificar
            excluir_id: ID de categoría a excluir de la búsqueda (útil para actualización)
            
        Returns:
            bool: True si existe, False si no
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if excluir_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM categorias WHERE nombre = ? AND id != ?",
                    (nombre.strip(), excluir_id)
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) FROM categorias WHERE nombre = ?",
                    (nombre.strip(),)
                )
            count = cursor.fetchone()[0]
            return count > 0


"""Repositorio para acceso a datos de información de tienda."""
import sqlite3
from contextlib import contextmanager
from typing import Optional

from ..domain.models import TiendaInfo


class TiendaRepository:
    """Repositorio para gestionar la información de la tienda."""
    
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
                CREATE TABLE IF NOT EXISTS tienda_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT
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
    
    def get_tienda_info(self) -> Optional[TiendaInfo]:
        """
        Obtiene la información de la tienda.
        
        Returns:
            TiendaInfo si existe, None si no hay información guardada
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, descripcion FROM tienda_info LIMIT 1")
            row = cursor.fetchone()
            if row:
                return TiendaInfo.from_tuple(row)
            return None
    
    def create_or_update_tienda_info(self, nombre: str, descripcion: Optional[str] = None) -> bool:
        """
        Crea o actualiza la información de la tienda.
        
        Args:
            nombre: Nombre de la tienda
            descripcion: Descripción de la tienda (opcional)
            
        Returns:
            bool: True si se guardó exitosamente
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya existe información
            cursor.execute("SELECT id FROM tienda_info LIMIT 1")
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar
                cursor.execute(
                    "UPDATE tienda_info SET nombre = ?, descripcion = ? WHERE id = ?",
                    (nombre, descripcion, existing[0])
                )
            else:
                # Crear
                cursor.execute(
                    "INSERT INTO tienda_info (nombre, descripcion) VALUES (?, ?)",
                    (nombre, descripcion)
                )
            
            conn.commit()
            return True


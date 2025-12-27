"""Repositorio para acceso a datos de clientes."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
from datetime import datetime

from ...config.settings import Settings
from ..domain.models import Cliente


class ClienteRepository:
    """Repositorio para gestionar clientes en la base de datos."""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa el repositorio.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path or Settings.DATABASE_PATH
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    documento TEXT,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    fecha_registro TIMESTAMP NOT NULL
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
    
    def create(self, cliente: Cliente) -> int:
        """
        Crea un nuevo cliente.
        
        Args:
            cliente: Cliente a crear
            
        Returns:
            int: ID del cliente creado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO clientes (nombre, documento, telefono, email, direccion, fecha_registro)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (cliente.nombre, cliente.documento, cliente.telefono, 
                 cliente.email, cliente.direccion, cliente.fecha_registro)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """
        Obtiene un cliente por su ID.
        
        Args:
            cliente_id: ID del cliente
            
        Returns:
            Cliente si existe, None en caso contrario
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_cliente(row)
            return None
    
    def get_all(self) -> List[Cliente]:
        """
        Obtiene todos los clientes.
        
        Returns:
            Lista de clientes
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes ORDER BY nombre")
            rows = cursor.fetchall()
            return [self._row_to_cliente(row) for row in rows]
    
    def search_by_name(self, nombre: str) -> List[Cliente]:
        """
        Busca clientes por nombre.
        
        Args:
            nombre: Nombre a buscar (parcial)
            
        Returns:
            Lista de clientes que coinciden
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM clientes WHERE nombre LIKE ? ORDER BY nombre",
                (f"%{nombre}%",)
            )
            rows = cursor.fetchall()
            return [self._row_to_cliente(row) for row in rows]
    
    def update(self, cliente: Cliente) -> bool:
        """
        Actualiza un cliente existente.
        
        Args:
            cliente: Cliente con datos actualizados
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clientes 
                SET nombre = ?, documento = ?, telefono = ?, email = ?, direccion = ?
                WHERE id = ?
            """, (cliente.nombre, cliente.documento, cliente.telefono,
                  cliente.email, cliente.direccion, cliente.id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete(self, cliente_id: int) -> bool:
        """
        Elimina un cliente por su ID.
        
        Args:
            cliente_id: ID del cliente a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_cliente(self, row: tuple) -> Cliente:
        """Convierte una fila de la BD a un objeto Cliente."""
        cliente_id, nombre, documento, telefono, email, direccion, fecha_registro = row
        
        if isinstance(fecha_registro, str):
            fecha = datetime.fromisoformat(fecha_registro)
        else:
            fecha = datetime.fromtimestamp(fecha_registro) if fecha_registro else datetime.now()
        
        return Cliente(
            id=cliente_id,
            nombre=nombre,
            documento=documento or "",
            telefono=telefono or "",
            email=email or "",
            direccion=direccion or "",
            fecha_registro=fecha
        )


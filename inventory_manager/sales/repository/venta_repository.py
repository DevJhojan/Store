"""Repositorio para acceso a datos de ventas."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
from datetime import datetime

from ...config.settings import Settings
from ..domain.models import Venta, ItemVenta


class VentaRepository:
    """Repositorio para gestionar ventas en la base de datos."""
    
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
            
            # Tabla de ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TIMESTAMP NOT NULL,
                    total REAL NOT NULL
                )
            """)
            
            # Tabla de items de venta
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    codigo_producto TEXT NOT NULL,
                    nombre_producto TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE
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
    
    def create(self, venta: Venta) -> int:
        """
        Crea una nueva venta en la base de datos.
        
        Args:
            venta: Venta a crear
            
        Returns:
            int: ID de la venta creada
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insertar venta
            cursor.execute(
                "INSERT INTO ventas (fecha, total) VALUES (?, ?)",
                (venta.fecha, venta.total)
            )
            venta_id = cursor.lastrowid
            
            # Insertar items
            for item in venta.items:
                cursor.execute(
                    """INSERT INTO items_venta 
                       (venta_id, codigo_producto, nombre_producto, cantidad, precio_unitario, subtotal)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (venta_id, item.codigo_producto, item.nombre_producto,
                     item.cantidad, item.precio_unitario, item.calcular_subtotal())
                )
            
            conn.commit()
            return venta_id
    
    def get_by_id(self, venta_id: int) -> Optional[Venta]:
        """
        Obtiene una venta por su ID.
        
        Args:
            venta_id: ID de la venta
            
        Returns:
            Venta si existe, None en caso contrario
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener venta
            cursor.execute("SELECT id, fecha, total FROM ventas WHERE id = ?", (venta_id,))
            venta_row = cursor.fetchone()
            
            if not venta_row:
                return None
            
            venta_id_db, fecha_str, total = venta_row
            
            # Obtener items
            cursor.execute("""
                SELECT codigo_producto, nombre_producto, cantidad, precio_unitario
                FROM items_venta
                WHERE venta_id = ?
            """, (venta_id,))
            
            items_data = cursor.fetchall()
            items = [
                ItemVenta(
                    codigo_producto=row[0],
                    nombre_producto=row[1],
                    cantidad=row[2],
                    precio_unitario=row[3]
                )
                for row in items_data
            ]
            
            # Parsear fecha
            if isinstance(fecha_str, str):
                fecha = datetime.fromisoformat(fecha_str)
            else:
                fecha = datetime.fromtimestamp(fecha_str) if fecha_str else datetime.now()
            
            return Venta(id=venta_id_db, fecha=fecha, items=items, total=total)
    
    def get_all(self) -> List[Venta]:
        """
        Obtiene todas las ventas.
        
        Returns:
            Lista de ventas
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM ventas ORDER BY fecha DESC")
            venta_ids = [row[0] for row in cursor.fetchall()]
            
            return [self.get_by_id(venta_id) for venta_id in venta_ids]


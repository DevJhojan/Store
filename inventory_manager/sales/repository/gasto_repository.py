"""Repositorio para acceso a datos de gastos operativos."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
from datetime import datetime, date

from ...config.settings import Settings
from ..domain.models import Gasto, MetodoPago


class GastoRepository:
    """Repositorio para gestionar gastos operativos en la base de datos."""
    
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
                CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TIMESTAMP NOT NULL,
                    categoria TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    monto REAL NOT NULL,
                    metodo_pago TEXT NOT NULL,
                    observaciones TEXT
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
    
    def create(self, gasto: Gasto) -> int:
        """
        Crea un nuevo gasto.
        
        Args:
            gasto: Gasto a crear
            
        Returns:
            int: ID del gasto creado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            metodo_pago_val = gasto.metodo_pago.value if isinstance(gasto.metodo_pago, MetodoPago) else gasto.metodo_pago
            cursor.execute(
                """INSERT INTO gastos (fecha, categoria, descripcion, monto, metodo_pago, observaciones)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (gasto.fecha, gasto.categoria, gasto.descripcion,
                 gasto.monto, metodo_pago_val, gasto.observaciones)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_by_id(self, gasto_id: int) -> Optional[Gasto]:
        """
        Obtiene un gasto por su ID.
        
        Args:
            gasto_id: ID del gasto
            
        Returns:
            Gasto si existe, None en caso contrario
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gastos WHERE id = ?", (gasto_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_gasto(row)
            return None
    
    def get_by_date_range(self, fecha_inicio: date, fecha_fin: date) -> List[Gasto]:
        """
        Obtiene gastos en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
            
        Returns:
            Lista de gastos
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM gastos 
                   WHERE DATE(fecha) >= ? AND DATE(fecha) <= ?
                   ORDER BY fecha DESC""",
                (fecha_inicio.isoformat(), fecha_fin.isoformat())
            )
            rows = cursor.fetchall()
            return [self._row_to_gasto(row) for row in rows]
    
    def get_by_date(self, fecha: date) -> List[Gasto]:
        """
        Obtiene gastos de una fecha específica.
        
        Args:
            fecha: Fecha a consultar
            
        Returns:
            Lista de gastos
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM gastos WHERE DATE(fecha) = ? ORDER BY fecha DESC",
                (fecha.isoformat(),)
            )
            rows = cursor.fetchall()
            return [self._row_to_gasto(row) for row in rows]
    
    def get_total_by_date(self, fecha: date) -> float:
        """
        Calcula el total de gastos de una fecha.
        
        Args:
            fecha: Fecha a consultar
            
        Returns:
            float: Total de gastos
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT SUM(monto) FROM gastos WHERE DATE(fecha) = ?",
                (fecha.isoformat(),)
            )
            result = cursor.fetchone()[0]
            return result if result else 0.0
    
    def get_all_categories(self) -> List[str]:
        """
        Obtiene todas las categorías de gastos únicas.
        
        Returns:
            Lista de categorías
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT categoria FROM gastos ORDER BY categoria")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
    
    def delete(self, gasto_id: int) -> bool:
        """
        Elimina un gasto por su ID.
        
        Args:
            gasto_id: ID del gasto a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_gasto(self, row: tuple) -> Gasto:
        """Convierte una fila de la BD a un objeto Gasto."""
        gasto_id, fecha_db, categoria, descripcion, monto, metodo_pago_str, observaciones = row
        
        if isinstance(fecha_db, str):
            fecha = datetime.fromisoformat(fecha_db)
        else:
            fecha = datetime.fromtimestamp(fecha_db) if fecha_db else datetime.now()
        
        try:
            metodo_pago = MetodoPago(metodo_pago_str)
        except ValueError:
            metodo_pago = MetodoPago.EFECTIVO
        
        return Gasto(
            id=gasto_id,
            fecha=fecha,
            categoria=categoria,
            descripcion=descripcion,
            monto=monto,
            metodo_pago=metodo_pago,
            observaciones=observaciones or ""
        )


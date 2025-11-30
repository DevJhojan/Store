"""Repositorio para acceso a datos de ventas."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
from datetime import datetime

from ...config.settings import Settings
from ..domain.models import Venta, ItemVenta, MetodoPago, MetodoPago


class VentaRepository:
    """Repositorio para gestionar ventas en la base de datos."""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa el repositorio.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        # Usar Ventas.DB como base de datos por defecto para ventas
        self.db_path = db_path or "Ventas.DB"
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_factura TEXT UNIQUE NOT NULL,
                    fecha TIMESTAMP NOT NULL,
                    cliente_id INTEGER,
                    subtotal REAL NOT NULL,
                    descuento_total REAL NOT NULL DEFAULT 0,
                    impuesto_total REAL NOT NULL DEFAULT 0,
                    total REAL NOT NULL,
                    metodo_pago TEXT NOT NULL,
                    observaciones TEXT,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
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
                    descuento REAL NOT NULL DEFAULT 0,
                    impuesto REAL NOT NULL DEFAULT 0,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE
                )
            """)
            
            # Tabla para configuración de numeración de facturas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuracion_factura (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            """)
            
            # Inicializar contador de facturas si no existe
            cursor.execute("SELECT valor FROM configuracion_factura WHERE clave = 'ultimo_numero'")
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO configuracion_factura (clave, valor) VALUES ('ultimo_numero', '0')"
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
    
    def generar_numero_factura(self) -> str:
        """
        Genera el siguiente número de factura incremental.
        
        Returns:
            str: Número de factura generado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener último número
            cursor.execute("SELECT valor FROM configuracion_factura WHERE clave = 'ultimo_numero'")
            row = cursor.fetchone()
            ultimo_numero = int(row[0]) if row else 0
            
            # Incrementar
            nuevo_numero = ultimo_numero + 1
            
            # Actualizar
            cursor.execute(
                "UPDATE configuracion_factura SET valor = ? WHERE clave = 'ultimo_numero'",
                (str(nuevo_numero),)
            )
            
            conn.commit()
            
            # Formato: FACT-00001
            return f"FACT-{nuevo_numero:05d}"
    
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
            
            # Generar número de factura si no tiene
            if not venta.numero_factura:
                venta.numero_factura = self.generar_numero_factura()
            
            # Calcular totales
            venta.calcular_total()
            
            # Obtener método de pago
            metodo_pago_val = (
                venta.metodo_pago.value 
                if isinstance(venta.metodo_pago, MetodoPago) 
                else str(venta.metodo_pago)
            )
            
            # Insertar venta
            cursor.execute(
                """INSERT INTO ventas 
                   (numero_factura, fecha, cliente_id, subtotal, descuento_total, 
                    impuesto_total, total, metodo_pago, observaciones)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (venta.numero_factura, venta.fecha, venta.cliente_id,
                 venta.subtotal, venta.descuento_total, venta.impuesto_total,
                 venta.total, metodo_pago_val, venta.observaciones)
            )
            venta_id = cursor.lastrowid
            
            # Insertar items
            for item in venta.items:
                cursor.execute(
                    """INSERT INTO items_venta 
                       (venta_id, codigo_producto, nombre_producto, cantidad, precio_unitario, 
                        descuento, impuesto, subtotal)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (venta_id, item.codigo_producto, item.nombre_producto,
                     item.cantidad, item.precio_unitario, item.descuento, item.impuesto,
                     item.calcular_total())
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
            
            # Obtener venta con todos los campos
            cursor.execute("""
                SELECT id, numero_factura, fecha, cliente_id, subtotal, descuento_total, 
                       impuesto_total, total, metodo_pago, observaciones
                FROM ventas WHERE id = ?
            """, (venta_id,))
            venta_row = cursor.fetchone()
            
            if not venta_row:
                return None
            
            (venta_id_db, numero_factura, fecha_str, cliente_id, subtotal, 
             descuento_total, impuesto_total, total, metodo_pago_str, observaciones) = venta_row
            
            # Obtener items con descuento e impuesto
            cursor.execute("""
                SELECT codigo_producto, nombre_producto, cantidad, precio_unitario, descuento, impuesto
                FROM items_venta
                WHERE venta_id = ?
            """, (venta_id,))
            
            items_data = cursor.fetchall()
            items = [
                ItemVenta(
                    codigo_producto=row[0],
                    nombre_producto=row[1],
                    cantidad=row[2],
                    precio_unitario=row[3],
                    descuento=row[4] if len(row) > 4 else 0.0,
                    impuesto=row[5] if len(row) > 5 else 0.0
                )
                for row in items_data
            ]
            
            # Parsear fecha
            if isinstance(fecha_str, str):
                fecha = datetime.fromisoformat(fecha_str)
            else:
                fecha = datetime.fromtimestamp(fecha_str) if fecha_str else datetime.now()
            
            # Parsear método de pago
            try:
                metodo_pago = MetodoPago(metodo_pago_str) if metodo_pago_str else MetodoPago.EFECTIVO
            except (ValueError, AttributeError):
                metodo_pago = MetodoPago.EFECTIVO
            
            return Venta(
                id=venta_id_db,
                numero_factura=numero_factura or "",
                fecha=fecha,
                items=items,
                cliente_id=cliente_id,
                subtotal=subtotal or 0.0,
                descuento_total=descuento_total or 0.0,
                impuesto_total=impuesto_total or 0.0,
                total=total or 0.0,
                metodo_pago=metodo_pago,
                observaciones=observaciones or ""
            )
    
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


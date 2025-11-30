"""Repositorio para consultar ventas con filtros avanzados."""
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
from datetime import datetime, date, time

from ...sales.domain.models import Venta, ItemVenta, MetodoPago


class VentaQueryRepository:
    """Repositorio para consultar ventas con filtros avanzados."""
    
    def __init__(self, db_path: str = "Ventas.DB"):
        """
        Inicializa el repositorio.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
    
    @contextmanager
    def _get_connection(self):
        """Context manager para obtener conexiones a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def obtener_ventas_filtradas(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        mes: Optional[int] = None,
        año: Optional[int] = None,
        hora_inicio: Optional[time] = None,
        hora_fin: Optional[time] = None
    ) -> List[Venta]:
        """
        Obtiene ventas con filtros avanzados.
        
        Args:
            fecha_inicio: Fecha de inicio (para rango de fechas o día específico)
            fecha_fin: Fecha de fin (para rango de fechas)
            mes: Mes específico (1-12)
            año: Año específico
            hora_inicio: Hora de inicio (para rango de horas)
            hora_fin: Hora de fin (para rango de horas)
            
        Returns:
            Lista de ventas que cumplen los filtros
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir query base
            query = """
                SELECT id, numero_factura, fecha, cliente_id, subtotal, descuento_total, 
                       impuesto_total, total, metodo_pago, observaciones
                FROM ventas
                WHERE 1=1
            """
            params = []
            
            # Filtro por día específico
            if fecha_inicio and not fecha_fin:
                query += " AND DATE(fecha) = ?"
                params.append(fecha_inicio.isoformat())
            
            # Filtro por rango de fechas
            elif fecha_inicio and fecha_fin:
                query += " AND DATE(fecha) >= ? AND DATE(fecha) <= ?"
                params.extend([fecha_inicio.isoformat(), fecha_fin.isoformat()])
            
            # Filtro por mes
            if mes is not None:
                query += " AND CAST(strftime('%m', fecha) AS INTEGER) = ?"
                params.append(mes)
            
            # Filtro por año
            if año is not None:
                query += " AND CAST(strftime('%Y', fecha) AS INTEGER) = ?"
                params.append(año)
            
            # Filtro por rango de horas (solo si hay fecha específica)
            if hora_inicio is not None or hora_fin is not None:
                if fecha_inicio and not fecha_fin:
                    # Si hay día específico, filtrar por horas de ese día
                    if hora_inicio:
                        query += " AND TIME(fecha) >= ?"
                        params.append(hora_inicio.strftime("%H:%M:%S"))
                    if hora_fin:
                        query += " AND TIME(fecha) <= ?"
                        params.append(hora_fin.strftime("%H:%M:%S"))
            
            query += " ORDER BY fecha DESC"
            
            cursor.execute(query, params)
            venta_rows = cursor.fetchall()
            
            # Obtener items para cada venta
            ventas = []
            for venta_row in venta_rows:
                venta_id = venta_row[0]
                
                # Obtener items usando id_venta (con fallback a venta_id para compatibilidad)
                try:
                    cursor.execute("""
                        SELECT codigo_producto, nombre_producto, cantidad, precio_unitario, descuento, impuesto
                        FROM items_venta
                        WHERE id_venta = ?
                        ORDER BY id
                    """, (venta_id,))
                except sqlite3.OperationalError:
                    # Si id_venta no existe, usar venta_id
                    cursor.execute("""
                        SELECT codigo_producto, nombre_producto, cantidad, precio_unitario, descuento, impuesto
                        FROM items_venta
                        WHERE venta_id = ?
                        ORDER BY id
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
                fecha_str = venta_row[2]
                fecha = None
                if isinstance(fecha_str, str):
                    try:
                        # Intentar formato ISO
                        fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    except:
                        try:
                            # Intentar formato timestamp
                            fecha = datetime.fromtimestamp(float(fecha_str))
                        except:
                            try:
                                # Intentar formato SQLite datetime
                                fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                            except:
                                fecha = datetime.now()
                else:
                    try:
                        fecha = datetime.fromtimestamp(fecha_str) if fecha_str else datetime.now()
                    except:
                        fecha = datetime.now()
                
                # Parsear método de pago
                metodo_pago_str = venta_row[8]
                try:
                    metodo_pago = MetodoPago(metodo_pago_str) if metodo_pago_str else MetodoPago.EFECTIVO
                except (ValueError, AttributeError):
                    metodo_pago = MetodoPago.EFECTIVO
                
                venta = Venta(
                    id=venta_id,
                    numero_factura=venta_row[1] or "",
                    fecha=fecha,
                    items=items,
                    cliente_id=venta_row[3],
                    subtotal=venta_row[4] or 0.0,
                    descuento_total=venta_row[5] or 0.0,
                    impuesto_total=venta_row[6] or 0.0,
                    total=venta_row[7] or 0.0,
                    metodo_pago=metodo_pago,
                    observaciones=venta_row[9] or ""
                )
                ventas.append(venta)
            
            return ventas
    
    def obtener_todas_las_ventas(self) -> List[Venta]:
        """Obtiene todas las ventas sin filtros."""
        return self.obtener_ventas_filtradas()
    
    def obtener_items_venta(self, venta_id: int) -> List[ItemVenta]:
        """
        Obtiene los items de una venta específica usando id_venta o venta_id.
        
        Args:
            venta_id: ID de la venta
            
        Returns:
            Lista de items de la venta
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si la columna id_venta existe
            cursor.execute("PRAGMA table_info(items_venta)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            has_id_venta = 'id_venta' in column_names
            
            # Usar la columna apropiada
            if has_id_venta:
                query = """
                    SELECT codigo_producto, nombre_producto, cantidad, precio_unitario, descuento, impuesto
                    FROM items_venta
                    WHERE id_venta = ?
                    ORDER BY id
                """
            else:
                query = """
                    SELECT codigo_producto, nombre_producto, cantidad, precio_unitario, descuento, impuesto
                    FROM items_venta
                    WHERE venta_id = ?
                    ORDER BY id
                """
            
            cursor.execute(query, (venta_id,))
            items_data = cursor.fetchall()
            
            items = [
                ItemVenta(
                    codigo_producto=row[0] or "",
                    nombre_producto=row[1] or "",
                    cantidad=row[2] if row[2] else 0,
                    precio_unitario=row[3] if row[3] else 0.0,
                    descuento=row[4] if len(row) > 4 and row[4] is not None else 0.0,
                    impuesto=row[5] if len(row) > 5 and row[5] is not None else 0.0
                )
                for row in items_data
            ]
            
            return items


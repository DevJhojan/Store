"""Servicio de lógica de negocio para Cierre de Caja."""
from typing import List, Optional
from datetime import date, time

from ..repository.venta_query_repository import VentaQueryRepository
from ...sales.domain.models import Venta, ItemVenta


class CashClosureService:
    """Servicio que contiene la lógica de negocio del cierre de caja."""
    
    def __init__(self, repository: Optional[VentaQueryRepository] = None):
        """
        Inicializa el servicio.
        
        Args:
            repository: Repositorio de consultas de ventas (si None, se crea uno nuevo)
        """
        self.repository = repository or VentaQueryRepository()
    
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
        return self.repository.obtener_ventas_filtradas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            mes=mes,
            año=año,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
    
    def calcular_total_ventas(self, ventas: List[Venta]) -> float:
        """
        Calcula el total de las ventas proporcionadas.
        
        Args:
            ventas: Lista de ventas
            
        Returns:
            float: Total de todas las ventas
        """
        return sum(venta.total for venta in ventas)
    
    def obtener_todas_las_ventas(self) -> List[Venta]:
        """Obtiene todas las ventas sin filtros."""
        return self.repository.obtener_todas_las_ventas()
    
    def obtener_items_venta(self, venta_id: int) -> List[ItemVenta]:
        """
        Obtiene los items de una venta específica.
        
        Args:
            venta_id: ID de la venta
            
        Returns:
            Lista de items de la venta
        """
        return self.repository.obtener_items_venta(venta_id)


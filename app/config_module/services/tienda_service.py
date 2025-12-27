"""Servicio para gestión de información de tienda."""
from typing import Optional

from ..domain.models import TiendaInfo
from ..repository.tienda_repository import TiendaRepository


class TiendaService:
    """Servicio para gestionar la información de la tienda."""
    
    def __init__(self, repository: TiendaRepository = None):
        """
        Inicializa el servicio.
        
        Args:
            repository: Repositorio de tienda (si None, se crea uno nuevo)
        """
        self.repository = repository or TiendaRepository()
    
    def obtener_informacion_tienda(self) -> Optional[TiendaInfo]:
        """
        Obtiene la información de la tienda.
        
        Returns:
            TiendaInfo si existe, None si no hay información guardada
        """
        return self.repository.get_tienda_info()
    
    def guardar_informacion_tienda(self, nombre: str, descripcion: Optional[str] = None) -> tuple[bool, str]:
        """
        Guarda la información de la tienda.
        
        Args:
            nombre: Nombre de la tienda
            descripcion: Descripción de la tienda (opcional)
            
        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        if not nombre or not nombre.strip():
            return False, "El nombre de la tienda es obligatorio."
        
        nombre = nombre.strip()
        descripcion = descripcion.strip() if descripcion else None
        
        exito = self.repository.create_or_update_tienda_info(nombre, descripcion)
        if exito:
            return True, "Información de la tienda guardada exitosamente."
        else:
            return False, "Error al guardar la información de la tienda."


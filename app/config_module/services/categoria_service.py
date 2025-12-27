"""Servicio para gestión de categorías."""
from typing import List, Optional, Tuple

from ..domain.models import Categoria
from ..repository.categoria_repository import CategoriaRepository


class CategoriaService:
    """Servicio para gestionar categorías."""
    
    def __init__(self, repository: Optional[CategoriaRepository] = None):
        """
        Inicializa el servicio.
        
        Args:
            repository: Repositorio de categorías (si None, se crea uno nuevo)
        """
        self.repository = repository or CategoriaRepository()
    
    def obtener_todas_las_categorias(self) -> List[Categoria]:
        """
        Obtiene todas las categorías.
        
        Returns:
            List[Categoria]: Lista de todas las categorías
        """
        return self.repository.get_all()
    
    def obtener_categoria_por_id(self, categoria_id: int) -> Optional[Categoria]:
        """
        Obtiene una categoría por su ID.
        
        Args:
            categoria_id: ID de la categoría
            
        Returns:
            Optional[Categoria]: La categoría si existe, None si no
        """
        return self.repository.get_by_id(categoria_id)
    
    def obtener_categoria_por_nombre(self, nombre: str) -> Optional[Categoria]:
        """
        Obtiene una categoría por su nombre.
        
        Args:
            nombre: Nombre de la categoría
            
        Returns:
            Optional[Categoria]: La categoría si existe, None si no
        """
        return self.repository.get_by_nombre(nombre)
    
    def agregar_categoria(self, nombre: str, descripcion: Optional[str] = None) -> Tuple[bool, str]:
        """
        Agrega una nueva categoría.
        
        Args:
            nombre: Nombre de la categoría
            descripcion: Descripción opcional de la categoría
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        categoria = Categoria(id=None, nombre=nombre, descripcion=descripcion)
        
        # Validar
        es_valido, mensaje_error = categoria.validar()
        if not es_valido:
            return False, mensaje_error
        
        # Verificar si ya existe
        if self.repository.existe_categoria(nombre):
            return False, f"Ya existe una categoría con el nombre '{nombre}'."
        
        # Crear
        exito = self.repository.create(categoria)
        if exito:
            return True, f"Categoría '{nombre}' agregada exitosamente."
        else:
            return False, f"Error al agregar la categoría '{nombre}'."
    
    def actualizar_categoria(self, categoria_id: int, nombre: str, 
                           descripcion: Optional[str] = None) -> Tuple[bool, str]:
        """
        Actualiza una categoría existente.
        
        Args:
            categoria_id: ID de la categoría a actualizar
            nombre: Nuevo nombre de la categoría
            descripcion: Nueva descripción de la categoría
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        categoria = Categoria(id=categoria_id, nombre=nombre, descripcion=descripcion)
        
        # Validar
        es_valido, mensaje_error = categoria.validar()
        if not es_valido:
            return False, mensaje_error
        
        # Verificar si el nombre ya existe en otra categoría
        if self.repository.existe_categoria(nombre, excluir_id=categoria_id):
            return False, f"Ya existe otra categoría con el nombre '{nombre}'."
        
        # Verificar que la categoría existe
        categoria_existente = self.repository.get_by_id(categoria_id)
        if not categoria_existente:
            return False, f"La categoría con ID {categoria_id} no existe."
        
        # Actualizar
        exito = self.repository.update(categoria)
        if exito:
            return True, f"Categoría '{nombre}' actualizada exitosamente."
        else:
            return False, f"Error al actualizar la categoría."
    
    def eliminar_categoria(self, categoria_id: int) -> Tuple[bool, str]:
        """
        Elimina una categoría.
        
        Args:
            categoria_id: ID de la categoría a eliminar
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        # Verificar que existe
        categoria = self.repository.get_by_id(categoria_id)
        if not categoria:
            return False, f"La categoría con ID {categoria_id} no existe."
        
        # Eliminar
        exito = self.repository.delete(categoria_id)
        if exito:
            return True, f"Categoría '{categoria.nombre}' eliminada exitosamente."
        else:
            return False, f"Error al eliminar la categoría."


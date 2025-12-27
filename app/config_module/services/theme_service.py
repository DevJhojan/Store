"""Servicio para gestión de temas."""
from ..repository.theme_repository import ThemeRepository


class ThemeService:
    """Servicio para gestionar el tema de la aplicación."""
    
    def __init__(self, repository: ThemeRepository = None):
        """
        Inicializa el servicio.
        
        Args:
            repository: Repositorio de temas (si None, se crea uno nuevo)
        """
        self.repository = repository or ThemeRepository()
    
    def obtener_tema_actual(self) -> str:
        """
        Obtiene el tema actual.
        
        Returns:
            str: Nombre del tema ('dark' o 'light')
        """
        return self.repository.get_theme()
    
    def cambiar_tema(self, theme: str) -> tuple[bool, str]:
        """
        Cambia el tema de la aplicación.
        
        Args:
            theme: Nombre del tema ('dark' o 'light')
            
        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        if theme not in ["dark", "light"]:
            return False, f"Tema '{theme}' no válido. Use 'dark' o 'light'."
        
        exito = self.repository.set_theme(theme)
        if exito:
            return True, f"Tema cambiado a '{theme}' exitosamente."
        else:
            return False, "Error al cambiar el tema."


"""Configuración del sistema de inventario."""


# Paleta de colores - Tema Dark con acentos rojos
COLORS = {
    "bg_darkest": "#0a0a0a",      # Fondo principal (casi negro)
    "bg_dark": "#121212",          # Fondo secundario
    "bg_medium": "#1a1a1a",        # Fondo de elementos
    "bg_light": "#242424",         # Fondo hover
    "red_primary": "#dc0000",      # Rojo principal
    "red_bright": "#ff1a1a",       # Rojo brillante (hover)
    "red_dark": "#8b0000",         # Rojo oscuro
    "red_glow": "#ff0000",         # Rojo para bordes/glow
    "text_primary": "#ffffff",     # Texto principal
    "text_secondary": "#b0b0b0",   # Texto secundario
    "text_muted": "#666666",       # Texto apagado
    "success": "#00ff00",          # Verde para valores positivos
}


class Settings:
    """Configuración general del sistema."""
    
    # Configuración de base de datos
    DATABASE_PATH: str = "inventario.db"
    
    # Configuración de interfaz
    WINDOW_TITLE: str = "⚡ Sistema de Gestión de Inventarios"
    WINDOW_GEOMETRY: str = "950x650"
    
    # Fuentes
    FONT_PRIMARY: str = "Consolas"
    FONT_SIZE_LARGE: int = 18
    FONT_SIZE_MEDIUM: int = 14
    FONT_SIZE_NORMAL: int = 11
    FONT_SIZE_SMALL: int = 10
    
    # Nombres de campos del formulario
    FIELD_NAMES = {
        "codigo": "Código",
        "nombre": "Nombre",
        "categoria": "Categoría",
        "cantidad": "Cantidad",
        "precio_unitario": "Precio Unitario"
    }


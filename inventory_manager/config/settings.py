"""Configuración del sistema de inventario."""


# Paleta de colores - Tema Dark con acentos rojos
COLORS_DARK = {
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

# Paleta de colores - Tema Light con acentos rojos
COLORS_LIGHT = {
    "bg_darkest": "#f5f5f5",       # Fondo principal (blanco suave)
    "bg_dark": "#ffffff",          # Fondo secundario (blanco)
    "bg_medium": "#e8e8e8",        # Fondo de elementos (gris claro)
    "bg_light": "#d0d0d0",         # Fondo hover (gris medio)
    "red_primary": "#dc0000",      # Rojo principal
    "red_bright": "#ff1a1a",       # Rojo brillante (hover)
    "red_dark": "#8b0000",         # Rojo oscuro
    "red_glow": "#ff0000",         # Rojo para bordes/glow
    "text_primary": "#000000",     # Texto principal (negro)
    "text_secondary": "#333333",   # Texto secundario (gris oscuro)
    "text_muted": "#666666",       # Texto apagado
    "success": "#00aa00",          # Verde para valores positivos
}

# Variable global para el tema actual (se inicializa con dark por defecto)
_current_theme = "dark"
COLORS = COLORS_DARK


def get_current_theme() -> str:
    """Obtiene el tema actual."""
    return _current_theme


def set_theme(theme: str):
    """
    Establece el tema actual.
    
    Args:
        theme: 'dark' o 'light'
    """
    global _current_theme, COLORS
    _current_theme = theme
    if theme == "light":
        COLORS = COLORS_LIGHT
    else:
        COLORS = COLORS_DARK


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


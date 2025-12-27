"""Utilidades para actualizar el tema de la aplicación."""
import tkinter as tk
from typing import Optional

from ...config.settings import COLORS, COLORS_DARK, COLORS_LIGHT
from typing import Optional


def _get_color_key_by_value(color_value: str, color_dict: dict) -> Optional[str]:
    """Obtiene la clave de un diccionario de colores por su valor."""
    for key, value in color_dict.items():
        if value == color_value:
            return key
    return None


def update_widget_colors(widget: tk.Widget, colors: dict = None):
    """
    Actualiza recursivamente los colores de un widget y sus hijos.
    
    Args:
        widget: Widget raíz a actualizar
        colors: Diccionario de colores (si None, usa COLORS global)
    """
    if colors is None:
        colors = COLORS
    
    # Mapeo completo de todos los colores posibles
    all_dark_colors = set(COLORS_DARK.values())
    all_light_colors = set(COLORS_LIGHT.values())
    
    # Actualizar colores del widget actual según su tipo
    widget_type = widget.winfo_class()
    
    try:
        # Para Frames
        if widget_type in ('Frame', 'TFrame'):
            try:
                current_bg = widget.cget('bg')
                # Si el color actual es de dark theme, cambiarlo al equivalente en el nuevo tema
                if current_bg in all_dark_colors:
                    key = _get_color_key_by_value(current_bg, COLORS_DARK)
                    if key:
                        widget.configure(bg=colors[key])
                elif current_bg in all_light_colors:
                    key = _get_color_key_by_value(current_bg, COLORS_LIGHT)
                    if key:
                        widget.configure(bg=colors[key])
            except:
                pass
        
        # Para Labels
        elif widget_type in ('Label', 'TLabel'):
            try:
                # Actualizar bg
                current_bg = widget.cget('bg')
                if current_bg in all_dark_colors:
                    key = _get_color_key_by_value(current_bg, COLORS_DARK)
                    if key:
                        widget.configure(bg=colors[key])
                elif current_bg in all_light_colors:
                    key = _get_color_key_by_value(current_bg, COLORS_LIGHT)
                    if key:
                        widget.configure(bg=colors[key])
                
                # Actualizar fg
                current_fg = widget.cget('fg')
                if current_fg in all_dark_colors:
                    key = _get_color_key_by_value(current_fg, COLORS_DARK)
                    if key:
                        widget.configure(fg=colors[key])
                elif current_fg in all_light_colors:
                    key = _get_color_key_by_value(current_fg, COLORS_LIGHT)
                    if key:
                        widget.configure(fg=colors[key])
                # Para texto, también verificar colores de texto específicos
                elif current_fg in ['#ffffff', '#b0b0b0', '#666666', '#000000', '#333333']:
                    fg_map = {
                        '#ffffff': colors['text_primary'],
                        '#b0b0b0': colors['text_secondary'],
                        '#666666': colors['text_muted'],
                        '#000000': colors['text_primary'],
                        '#333333': colors['text_secondary'],
                    }
                    if current_fg in fg_map:
                        widget.configure(fg=fg_map[current_fg])
            except:
                pass
        
        # Para Entry
        elif widget_type in ('Entry', 'TEntry'):
            try:
                widget.configure(
                    bg=colors['bg_medium'],
                    fg=colors['text_primary'],
                    insertbackground=colors['text_primary']
                )
            except:
                pass
        
        # Para Text
        elif widget_type == 'Text':
            try:
                widget.configure(
                    bg=colors['bg_medium'],
                    fg=colors['text_primary'],
                    insertbackground=colors['text_primary']
                )
            except:
                pass
        
        # Para Button - mantener botones rojos (acento) como están
        elif widget_type == 'Button':
            try:
                current_bg = widget.cget('bg')
                # Si es un color rojo (botón de acento), mantenerlo
                if current_bg in ['#dc0000', '#ff1a1a', '#8b0000', '#ff0000']:
                    pass
                else:
                    # Actualizar otros botones
                    if current_bg in all_dark_colors:
                        key = _get_color_key_by_value(current_bg, COLORS_DARK)
                        if key:
                            widget.configure(bg=colors[key])
                    elif current_bg in all_light_colors:
                        key = _get_color_key_by_value(current_bg, COLORS_LIGHT)
                        if key:
                            widget.configure(bg=colors[key])
                    
                    # Actualizar fg de botones
                    try:
                        current_fg = widget.cget('fg')
                        if current_fg in ['#ffffff', '#b0b0b0', '#000000', '#333333']:
                            widget.configure(fg=colors['text_primary'])
                    except:
                        pass
            except:
                pass
        
        # Para Canvas
        elif widget_type == 'Canvas':
            try:
                widget.configure(bg=colors['bg_darkest'])
            except:
                pass
        
    except Exception:
        # Si hay algún error, continuar con los hijos
        pass
    
    # Actualizar recursivamente los hijos
    try:
        for child in widget.winfo_children():
            update_widget_colors(child, colors)
    except:
        pass


def update_application_theme(root: tk.Widget, style_manager=None):
    """
    Actualiza el tema de toda la aplicación.
    
    Args:
        root: Widget raíz de la aplicación
        style_manager: StyleManager opcional para recargar estilos
    """
    from ...config.settings import COLORS
    
    # Recargar estilos si se proporciona el style_manager
    if style_manager:
        style_manager.setup_styles()
    
    # Actualizar todos los widgets recursivamente
    update_widget_colors(root, COLORS)

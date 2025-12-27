"""Utilidades para actualizar el tema de la aplicación."""
import tkinter as tk
from typing import Optional

from ...config.settings import COLORS, COLORS_DARK, COLORS_LIGHT


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
    
    # Mapeo completo de todos los colores posibles (dark -> nuevo tema, light -> nuevo tema)
    all_dark_colors = set(COLORS_DARK.values())
    all_light_colors = set(COLORS_LIGHT.values())
    
    # Crear mapeo bidireccional de colores antiguos a nuevos
    color_mapping = {}
    for key in COLORS_DARK.keys():
        # Mapear desde dark theme al nuevo tema
        color_mapping[COLORS_DARK[key]] = colors[key]
        # Mapear desde light theme al nuevo tema
        color_mapping[COLORS_LIGHT[key]] = colors[key]
    
    # Actualizar colores del widget actual según su tipo
    widget_type = widget.winfo_class()
    
    try:
        # Para Frames - Actualizar SIEMPRE si el color no coincide con el nuevo tema
        if widget_type in ('Frame', 'TFrame'):
            try:
                current_bg = widget.cget('bg')
                # Si el color actual NO es del nuevo tema, actualizarlo
                if current_bg not in colors.values():
                    # Si el color actual está en el mapeo, actualizarlo directamente
                    if current_bg in color_mapping:
                        widget.configure(bg=color_mapping[current_bg])
                    # También verificar si está en los diccionarios de temas originales
                    elif current_bg in all_dark_colors:
                        key = _get_color_key_by_value(current_bg, COLORS_DARK)
                        if key and key in colors:
                            widget.configure(bg=colors[key])
                    elif current_bg in all_light_colors:
                        key = _get_color_key_by_value(current_bg, COLORS_LIGHT)
                        if key and key in colors:
                            widget.configure(bg=colors[key])
                    # Si no coincide con ningún tema, intentar usar bg_darkest como fallback
                    else:
                        # Intentar usar el mismo color del padre si existe
                        try:
                            if widget.master:
                                parent_bg = widget.master.cget('bg')
                                if parent_bg in colors.values():
                                    widget.configure(bg=parent_bg)
                                else:
                                    widget.configure(bg=colors['bg_darkest'])
                            else:
                                widget.configure(bg=colors['bg_darkest'])
                        except:
                            widget.configure(bg=colors['bg_darkest'])
            except (tk.TclError, AttributeError):
                pass
        
        # Para Labels - Actualizar SIEMPRE si los colores no coinciden
        elif widget_type in ('Label', 'TLabel'):
            try:
                # Actualizar bg
                current_bg = widget.cget('bg')
                if current_bg not in colors.values():
                    if current_bg in color_mapping:
                        widget.configure(bg=color_mapping[current_bg])
                    elif current_bg in all_dark_colors:
                        key = _get_color_key_by_value(current_bg, COLORS_DARK)
                        if key and key in colors:
                            widget.configure(bg=colors[key])
                    elif current_bg in all_light_colors:
                        key = _get_color_key_by_value(current_bg, COLORS_LIGHT)
                        if key and key in colors:
                            widget.configure(bg=colors[key])
                
                # Actualizar fg
                current_fg = widget.cget('fg')
                # Verificar si el fg actual NO es del nuevo tema
                if current_fg not in colors.values():
                    if current_fg in color_mapping:
                        widget.configure(fg=color_mapping[current_fg])
                    elif current_fg in all_dark_colors:
                        key = _get_color_key_by_value(current_fg, COLORS_DARK)
                        if key and key in colors:
                            widget.configure(fg=colors[key])
                    elif current_fg in all_light_colors:
                        key = _get_color_key_by_value(current_fg, COLORS_LIGHT)
                        if key and key in colors:
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
            except (tk.TclError, AttributeError):
                pass
        
        # Para Entry - SIEMPRE actualizar, ya que siempre usan bg_medium
        elif widget_type in ('Entry', 'TEntry'):
            try:
                widget.configure(
                    bg=colors['bg_medium'],
                    fg=colors['text_primary'],
                    insertbackground=colors['text_primary']
                )
                # También actualizar readonlybackground si existe
                try:
                    widget.configure(readonlybackground=colors['bg_medium'])
                except:
                    pass
            except (tk.TclError, AttributeError):
                pass
        
        # Para Text - SIEMPRE actualizar
        elif widget_type == 'Text':
            try:
                widget.configure(
                    bg=colors['bg_medium'],
                    fg=colors['text_primary'],
                    insertbackground=colors['text_primary']
                )
            except (tk.TclError, AttributeError):
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
                    if current_bg in color_mapping:
                        widget.configure(bg=color_mapping[current_bg])
                    elif current_bg in all_dark_colors:
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
                        if current_fg in color_mapping:
                            widget.configure(fg=color_mapping[current_fg])
                        elif current_fg in ['#ffffff', '#b0b0b0', '#000000', '#333333']:
                            widget.configure(fg=colors['text_primary'])
                    except:
                        pass
            except:
                pass
        
        # Para Canvas - SIEMPRE actualizar a bg_darkest
        elif widget_type == 'Canvas':
            try:
                widget.configure(bg=colors['bg_darkest'])
            except (tk.TclError, AttributeError):
                pass
        
    except Exception:
        # Si hay algún error, continuar con los hijos
        pass
    
    # Actualizar recursivamente los hijos
    try:
        children = widget.winfo_children()
        for child in children:
            update_widget_colors(child, colors)
    except (tk.TclError, AttributeError):
        pass


def update_application_theme(root: tk.Widget, style_manager=None):
    """
    Actualiza el tema de toda la aplicación.
    
    Args:
        root: Widget raíz de la aplicación
        style_manager: StyleManager opcional para recargar estilos
    """
    from ...config.settings import COLORS
    from tkinter import ttk
    
    # Recargar estilos si se proporciona el style_manager
    if style_manager:
        style_manager.setup_styles()
    
    # También actualizar estilos de ttk.Style manualmente
    style = ttk.Style()
    c = COLORS
    
    # Actualizar estilos de ttk
    try:
        style.configure("TCombobox", fieldbackground=c["bg_medium"], foreground=c["text_primary"])
    except:
        pass
    
    # Forzar actualización del root primero
    try:
        if hasattr(root, 'configure'):
            try:
                root_bg = root.cget('bg')
                # Actualizar el root si el color no es del nuevo tema
                if root_bg not in COLORS.values():
                    root.configure(bg=COLORS['bg_darkest'])
            except:
                try:
                    root.configure(bg=COLORS['bg_darkest'])
                except:
                    pass
    except:
        pass
    
    # Actualizar todos los widgets recursivamente
    update_widget_colors(root, COLORS)

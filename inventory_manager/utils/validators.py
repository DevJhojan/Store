"""Utilidades de validación."""
from typing import Dict, Tuple, Optional, Any


def validate_fields(entries: Dict[str, Any], field_names: Dict[str, str]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Valida que todos los campos de un formulario estén llenos.
    
    Args:
        entries: Diccionario de campos de entrada (tkinter Entry)
        field_names: Diccionario que mapea keys a nombres legibles
        
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (es_valido, key_campo_vacio, nombre_campo_vacio)
    """
    for key, entry in entries.items():
        if not entry.get().strip():
            nombre_legible = field_names.get(key, key)
            return False, key, nombre_legible
    return True, None, None


def parse_numeric_field(value: str, field_type: type = int) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Parsea un campo numérico y valida su formato.
    
    Args:
        value: Valor a parsear
        field_type: Tipo numérico (int o float)
        
    Returns:
        Tuple[bool, Optional[any], Optional[str]]: (exitoso, valor_parseado, mensaje_error)
    """
    try:
        value_clean = value.strip()
        if not value_clean:
            return False, None, "El campo no puede estar vacío."
        
        if field_type == int:
            parsed = int(value_clean)
        elif field_type == float:
            parsed = float(value_clean)
        else:
            return False, None, "Tipo numérico no soportado."
        
        if parsed < 0:
            return False, None, "El valor debe ser mayor o igual a 0."
        
        return True, parsed, None
        
    except ValueError:
        tipo_nombre = "entero" if field_type == int else "decimal"
        return False, None, f"El valor debe ser un número {tipo_nombre} válido."


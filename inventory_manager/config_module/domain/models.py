"""Modelos de dominio para el módulo de configuración."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Categoria:
    """Modelo de categoría."""
    id: Optional[int]
    nombre: str
    descripcion: Optional[str] = None

    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Categoria":
        """Crea un modelo desde un diccionario."""
        return cls(
            id=data.get("id"),
            nombre=data["nombre"],
            descripcion=data.get("descripcion")
        )

    @classmethod
    def from_tuple(cls, data: tuple) -> "Categoria":
        """Crea un modelo desde una tupla de base de datos."""
        return cls(
            id=data[0],
            nombre=data[1],
            descripcion=data[2] if len(data) > 2 else None
        )


@dataclass
class TiendaInfo:
    """Modelo de información de la tienda."""
    id: Optional[int]
    nombre: str
    descripcion: Optional[str] = None

    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TiendaInfo":
        """Crea un modelo desde un diccionario."""
        return cls(
            id=data.get("id"),
            nombre=data["nombre"],
            descripcion=data.get("descripcion")
        )

    @classmethod
    def from_tuple(cls, data: tuple) -> "TiendaInfo":
        """Crea un modelo desde una tupla de base de datos."""
        return cls(
            id=data[0],
            nombre=data[1],
            descripcion=data[2] if len(data) > 2 else None
        )

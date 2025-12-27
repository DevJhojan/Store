"""Repositorio para acceso a datos de temas."""
import sqlite3
from contextlib import contextmanager


class ThemeRepository:
    """Repositorio para gestionar el tema de la aplicación."""
    
    def __init__(self, db_path: str = "inventario.db"):
        """
        Inicializa el repositorio.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()
            
            # Inicializar tema por defecto si no existe
            cursor.execute("SELECT value FROM app_settings WHERE key = 'theme'")
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO app_settings (key, value) VALUES (?, ?)",
                    ("theme", "dark")
                )
                conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para obtener conexiones a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def get_theme(self) -> str:
        """
        Obtiene el tema actual.
        
        Returns:
            str: Nombre del tema ('dark' o 'light')
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = 'theme'")
            row = cursor.fetchone()
            return row[0] if row else "dark"
    
    def set_theme(self, theme: str) -> bool:
        """
        Establece el tema.
        
        Args:
            theme: Nombre del tema ('dark' o 'light')
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        if theme not in ["dark", "light"]:
            return False
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
                ("theme", theme)
            )
            conn.commit()
            return True


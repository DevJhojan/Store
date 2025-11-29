"""Gestor de estilos para la interfaz gráfica."""
from tkinter import ttk

from ..config.settings import COLORS


class StyleManager:
    """Gestiona los estilos de la interfaz gráfica."""
    
    def __init__(self):
        """Inicializa y configura los estilos."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.setup_styles()
    
    def setup_styles(self):
        """Configura todos los estilos personalizados."""
        c = COLORS
        
        # Estilo para Treeview
        self.style.configure(
            "Custom.Treeview",
            background=c["bg_dark"],
            foreground=c["text_primary"],
            fieldbackground=c["bg_dark"],
            rowheight=32,
            font=("Consolas", 10),
            borderwidth=0
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background=c["red_dark"],
            foreground=c["text_primary"],
            font=("Consolas", 10, "bold"),
            borderwidth=1,
            relief="flat"
        )
        self.style.map(
            "Custom.Treeview",
            background=[("selected", c["red_primary"])],
            foreground=[("selected", c["text_primary"])]
        )
        self.style.map(
            "Custom.Treeview.Heading",
            background=[("active", c["red_primary"])]
        )
        
        # Estilo para botones principales (rojo)
        self.style.configure(
            "Accent.TButton",
            background=c["red_primary"],
            foreground=c["text_primary"],
            font=("Consolas", 10, "bold"),
            padding=(18, 10),
            borderwidth=2
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", c["red_bright"]), ("pressed", c["red_dark"])]
        )
        
        # Estilo para botones secundarios (oscuros con borde rojo)
        self.style.configure(
            "Secondary.TButton",
            background=c["bg_medium"],
            foreground=c["text_primary"],
            font=("Consolas", 10),
            padding=(18, 10),
            borderwidth=2
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", c["bg_light"]), ("pressed", c["bg_dark"])]
        )
        
        # Estilo para scrollbar
        self.style.configure(
            "Custom.Vertical.TScrollbar",
            background=c["bg_medium"],
            troughcolor=c["bg_dark"],
            borderwidth=0,
            arrowcolor=c["red_primary"]
        )
        self.style.map(
            "Custom.Vertical.TScrollbar",
            background=[("active", c["red_primary"])]
        )


"""Ventana principal del sistema que permite acceder a los diferentes módulos."""
import tkinter as tk
from tkinter import ttk

from .config.settings import Settings, COLORS
from .ui.styles import StyleManager
from .inventory.ui.views import InventoryGUI
from .sales.ui.views import SalesGUI


class MainWindow:
    """Ventana principal del sistema."""
    
    def __init__(self, root: tk.Tk):
        """
        Inicializa la ventana principal.
        
        Args:
            root: Ventana raíz de tkinter
        """
        self.root = root
        self.root.title("🏪 Sistema de Gestión - Store")
        self.root.configure(bg=COLORS["bg_darkest"])
        self.root.resizable(True, True)  # Permitir redimensionar
        
        # Maximizar la ventana principal (compatible con todos los sistemas)
        try:
            # Intentar maximizar en Linux
            self.root.attributes('-zoomed', True)
        except:
            try:
                # Intentar maximizar en Windows
                self.root.state('zoomed')
            except:
                # Si nada funciona, obtener tamaño de pantalla y establecer geometría
                self.root.update_idletasks()
                width = self.root.winfo_screenwidth()
                height = self.root.winfo_screenheight()
                self.root.geometry(f"{width}x{height}")
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Referencias a ventanas abiertas
        self.inventory_window = None
        self.sales_window = None
        
        # Crear interfaz
        self.create_widgets()
    
    def create_widgets(self):
        """Crear todos los widgets de la ventana principal."""
        c = COLORS
        
        # Frame principal con scroll si es necesario
        main_frame = tk.Frame(self.root, bg=c["bg_darkest"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        # Título principal
        title_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        title_frame.pack(fill=tk.X, pady=(0, 40))
        
        # Línea decorativa superior
        tk.Frame(title_frame, bg=c["red_primary"], height=3).pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            title_frame,
            text="◆ SISTEMA DE GESTIÓN - STORE ◆",
            font=(Settings.FONT_PRIMARY, 22, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="[ Plataforma Integrada de Gestión ]",
            font=(Settings.FONT_PRIMARY, 11),
            fg=c["text_muted"],
            bg=c["bg_darkest"]
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Línea decorativa inferior
        tk.Frame(title_frame, bg=c["red_primary"], height=3).pack(fill=tk.X, pady=(15, 0))
        
        # Frame para módulos - usando pack para asegurar visibilidad
        modules_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        modules_frame.pack(fill=tk.BOTH, expand=True)
        
        # Módulo de Inventarios
        self.create_module_card(
            modules_frame,
            "📦 GESTIÓN DE INVENTARIOS",
            "Administra productos, stock y precios del inventario.",
            self.open_inventory,
            c
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Separador visible
        separator = tk.Frame(modules_frame, bg=c["red_primary"], height=2)
        separator.pack(fill=tk.X, pady=15, padx=20)
        
        # Módulo de Ventas
        self.create_module_card(
            modules_frame,
            "💰 GESTIÓN DE VENTAS",
            "Registra ventas y actualiza automáticamente el inventario.",
            self.open_sales,
            c
        ).pack(fill=tk.X, pady=(0, 0))
        
        # Frame para footer
        footer_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        footer_frame.pack(fill=tk.X, pady=(30, 0))
        
        footer_label = tk.Label(
            footer_frame,
            text="Seleccione un módulo para comenzar",
            font=(Settings.FONT_PRIMARY, 9),
            fg=c["text_muted"],
            bg=c["bg_darkest"]
        )
        footer_label.pack()
    
    def create_module_card(self, parent: tk.Frame, title: str, description: str, 
                          command, colors: dict):
        """Crea una tarjeta de módulo y retorna el contenedor."""
        # Contenedor de tarjeta
        card_container = tk.Frame(parent, bg=colors["red_dark"], padx=2, pady=2)
        
        card_frame = tk.Frame(card_container, bg=colors["bg_dark"], padx=30, pady=25)
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título del módulo
        title_label = tk.Label(
            card_frame,
            text=title,
            font=(Settings.FONT_PRIMARY, 14, "bold"),
            fg=colors["red_primary"],
            bg=colors["bg_dark"]
        )
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Descripción
        desc_label = tk.Label(
            card_frame,
            text=description,
            font=(Settings.FONT_PRIMARY, 10),
            fg=colors["text_secondary"],
            bg=colors["bg_dark"],
            justify=tk.LEFT,
            wraplength=450
        )
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Botón para abrir módulo
        btn = ttk.Button(
            card_frame,
            text="▶ Abrir Módulo",
            command=command,
            style="Accent.TButton"
        )
        btn.pack(anchor="w")
        
        return card_container
    
    def open_inventory(self):
        """Abre el módulo de Inventarios."""
        if self.inventory_window is None or not self.inventory_window.window.winfo_exists():
            self.inventory_window = InventoryGUI(self.root)
            # Configurar callback cuando se cierre
            self.inventory_window.window.protocol(
                "WM_DELETE_WINDOW",
                lambda: self.on_inventory_close()
            )
            # Pasar referencia para notificaciones bidireccionales
            if self.sales_window and hasattr(self.sales_window, 'window') and self.sales_window.window.winfo_exists():
                self.sales_window.inventory_gui_ref = self.inventory_window
        else:
            self.inventory_window.window.lift()
            self.inventory_window.window.focus()
    
    def open_sales(self):
        """Abre el módulo de Ventas."""
        if self.sales_window is None or not self.sales_window.window.winfo_exists():
            self.sales_window = SalesGUI(self.root)
            # Configurar callback cuando se cierre
            self.sales_window.window.protocol(
                "WM_DELETE_WINDOW",
                lambda: self.on_sales_close()
            )
            # Pasar referencia al inventario si está abierto
            if self.inventory_window and hasattr(self.inventory_window, 'window') and self.inventory_window.window.winfo_exists():
                self.sales_window.inventory_gui_ref = self.inventory_window
        else:
            self.sales_window.window.lift()
            self.sales_window.window.focus()
    
    def on_inventory_close(self):
        """Maneja el cierre de la ventana de inventarios."""
        if self.inventory_window:
            self.inventory_window.window.destroy()
            self.inventory_window = None
            # Limpiar referencia en ventas
            if self.sales_window:
                self.sales_window.inventory_gui_ref = None
    
    def on_sales_close(self):
        """Maneja el cierre de la ventana de ventas."""
        if self.sales_window:
            self.sales_window.window.destroy()
            self.sales_window = None


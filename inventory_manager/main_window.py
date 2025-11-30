"""Ventana principal del sistema que permite acceder a los diferentes módulos."""
import tkinter as tk
from tkinter import ttk

from .config.settings import Settings, COLORS
from .ui.styles import StyleManager
from .inventory.ui.views import InventoryGUI
from .sales.ui.views import SalesGUI
from .cash_closure.ui.views import CashClosureGUI


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
        self.cash_closure_window = None
        
        # Crear interfaz
        self.create_widgets()
    
    def create_widgets(self):
        """Crear todos los widgets de la ventana principal con scrollbar."""
        c = COLORS
        
        # Canvas principal para scrollbar
        canvas = tk.Canvas(
            self.root,
            bg=c["bg_darkest"],
            highlightthickness=0
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar vertical estilizada
        v_scrollbar = ttk.Scrollbar(
            self.root,
            orient=tk.VERTICAL,
            command=canvas.yview,
            style="Custom.Vertical.TScrollbar"
        )
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Frame scrollable dentro del canvas
        scrollable_frame = tk.Frame(canvas, bg=c["bg_darkest"])
        canvas_window = canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )
        
        # Configurar scroll del canvas
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Habilitar scroll con rueda del mouse (Windows/Mac)
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Habilitar scroll con rueda del mouse (Linux)
        def on_button4(event):
            canvas.yview_scroll(-1, "units")
        
        def on_button5(event):
            canvas.yview_scroll(1, "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_button4)
        canvas.bind_all("<Button-5>", on_button5)
        
        # Guardar referencia al canvas
        self.canvas = canvas
        
        # Frame principal dentro del scrollable (con padding)
        main_frame = tk.Frame(scrollable_frame, bg=c["bg_darkest"])
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
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Separador visible
        separator2 = tk.Frame(modules_frame, bg=c["red_primary"], height=2)
        separator2.pack(fill=tk.X, pady=15, padx=20)
        
        # Módulo de Cierre de Caja
        self.create_module_card(
            modules_frame,
            "💵 CIERRE DE CAJA",
            "Consulta y analiza todas las ventas registradas con filtros avanzados.",
            self.open_cash_closure,
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
    
    def open_cash_closure(self):
        """Abre el módulo de Cierre de Caja."""
        if self.cash_closure_window is None or not self.cash_closure_window.window.winfo_exists():
            self.cash_closure_window = CashClosureGUI(self.root)
            # Configurar callback cuando se cierre
            self.cash_closure_window.window.protocol(
                "WM_DELETE_WINDOW",
                lambda: self.on_cash_closure_close()
            )
        else:
            self.cash_closure_window.window.lift()
            self.cash_closure_window.window.focus()
    
    def on_sales_close(self):
        """Maneja el cierre de la ventana de ventas."""
        if self.sales_window:
            self.sales_window.window.destroy()
            self.sales_window = None
    
    def on_cash_closure_close(self):
        """Maneja el cierre de la ventana de cierre de caja."""
        if self.cash_closure_window:
            self.cash_closure_window.window.destroy()
            self.cash_closure_window = None


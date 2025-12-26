"""Ventana principal del sistema que permite acceder a los diferentes módulos."""
import tkinter as tk
from tkinter import ttk
import webbrowser
from datetime import datetime, date

from .config.settings import Settings, COLORS
from .ui.styles import StyleManager
from .inventory.ui.views import InventoryGUI
from .sales.ui.views import SalesGUI
from .cash_closure.ui.views import CashClosureGUI
from .repository.product_repository import ProductRepository
from .sales.repository.venta_repository import VentaRepository
from .services.inventory_service import InventoryService
from .cash_closure.services.cash_closure_service import CashClosureService


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
        
        # Inicializar servicios para obtener datos del resumen
        self.product_repository = ProductRepository()
        self.venta_repository = VentaRepository()
        self.inventory_service = InventoryService(self.product_repository)
        self.cash_closure_service = CashClosureService()
        
        # Crear interfaz
        self.create_widgets()
        
        # Actualizar resumen
        self.update_summary()
    
    def create_widgets(self):
        """Crear todos los widgets de la ventana principal con resumen y navegación."""
        c = COLORS
        
        # Frame principal (sin scrollbar ya que es un resumen compacto)
        main_container = tk.Frame(self.root, bg=c["bg_darkest"])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Frame para el botón de GitHub en la esquina superior derecha
        github_frame = tk.Frame(self.root, bg=c["bg_darkest"])
        github_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        # Botón de GitHub
        github_btn = tk.Button(
            github_frame,
            text="🐙",
            font=(Settings.FONT_PRIMARY, 20),
            bg=c["bg_dark"],
            fg=c["text_secondary"],
            activebackground=c["red_dark"],
            activeforeground=c["red_primary"],
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.open_github
        )
        github_btn.pack()
        
        # Tooltip al pasar el mouse
        def on_enter(event):
            github_btn.config(bg=c["red_dark"], fg=c["red_primary"])
        
        def on_leave(event):
            github_btn.config(bg=c["bg_dark"], fg=c["text_secondary"])
        
        github_btn.bind("<Enter>", on_enter)
        github_btn.bind("<Leave>", on_leave)
        
        # Frame para contenido principal (resumen)
        content_frame = tk.Frame(main_container, bg=c["bg_darkest"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Título principal
        title_frame = tk.Frame(content_frame, bg=c["bg_darkest"])
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Línea decorativa superior
        tk.Frame(title_frame, bg=c["red_primary"], height=3).pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            title_frame,
            text="◆ RESUMEN DEL SISTEMA DE GESTIÓN ◆",
            font=(Settings.FONT_PRIMARY, 20, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="[ Vista General de la Operación ]",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_muted"],
            bg=c["bg_darkest"]
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Línea decorativa inferior
        tk.Frame(title_frame, bg=c["red_primary"], height=3).pack(fill=tk.X, pady=(15, 0))
        
        # Frame para las tarjetas de resumen
        summary_frame = tk.Frame(content_frame, bg=c["bg_darkest"])
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Crear tarjetas de resumen (se actualizarán con datos reales)
        self.create_summary_cards(summary_frame, c)
        
        # Button bar de navegación en la parte inferior
        self.create_navigation_bar(main_container, c)
    
    def get_summary_data(self):
        """Obtiene los datos del resumen del sistema."""
        try:
            # Datos de inventario
            productos = self.product_repository.get_all()
            total_productos = len(productos)
            valor_total_inventario = self.product_repository.calculate_total_value()
            productos_bajo_stock = sum(1 for p in productos if p.cantidad < 10)
            
            # Datos de ventas
            ventas = self.venta_repository.get_all()
            total_ventas = len(ventas)
            total_ingresos = sum(v.total for v in ventas)
            
            # Ventas del día
            hoy = date.today()
            ventas_hoy = [
                v for v in ventas 
                if isinstance(v.fecha, datetime) and v.fecha.date() == hoy
            ]
            ingresos_hoy = sum(v.total for v in ventas_hoy)
            
            # Ventas del mes
            mes_actual = hoy.month
            año_actual = hoy.year
            ventas_mes = [
                v for v in ventas
                if isinstance(v.fecha, datetime) and 
                   v.fecha.date().month == mes_actual and 
                   v.fecha.date().year == año_actual
            ]
            ingresos_mes = sum(v.total for v in ventas_mes)
            
            return {
                "total_productos": total_productos,
                "valor_total_inventario": valor_total_inventario,
                "productos_bajo_stock": productos_bajo_stock,
                "total_ventas": total_ventas,
                "total_ingresos": total_ingresos,
                "ventas_hoy": len(ventas_hoy),
                "ingresos_hoy": ingresos_hoy,
                "ventas_mes": len(ventas_mes),
                "ingresos_mes": ingresos_mes
            }
        except Exception as e:
            # En caso de error, retornar valores por defecto
            return {
                "total_productos": 0,
                "valor_total_inventario": 0.0,
                "productos_bajo_stock": 0,
                "total_ventas": 0,
                "total_ingresos": 0.0,
                "ventas_hoy": 0,
                "ingresos_hoy": 0.0,
                "ventas_mes": 0,
                "ingresos_mes": 0.0
            }
    
    def create_summary_cards(self, parent: tk.Frame, colors: dict):
        """Crea las tarjetas de resumen con estadísticas."""
        # Frame para las tarjetas (grid layout)
        cards_container = tk.Frame(parent, bg=colors["bg_darkest"])
        cards_container.pack(fill=tk.BOTH, expand=True)
        
        # Guardar referencia para actualizar
        self.summary_cards_frame = cards_container
        self.summary_colors = colors
        
        # Crear tarjetas (se actualizarán con datos reales en update_summary)
        self.inventory_card = self.create_summary_card(
            cards_container, "📦 Inventario", "", colors, 0, 0
        )
        self.sales_card = self.create_summary_card(
            cards_container, "💰 Ventas", "", colors, 0, 1
        )
        self.daily_card = self.create_summary_card(
            cards_container, "📊 Hoy", "", colors, 1, 0
        )
        self.monthly_card = self.create_summary_card(
            cards_container, "📈 Mes Actual", "", colors, 1, 1
        )
        
        # Configurar grid
        cards_container.grid_columnconfigure(0, weight=1, uniform="cards")
        cards_container.grid_columnconfigure(1, weight=1, uniform="cards")
        cards_container.grid_rowconfigure(0, weight=1)
        cards_container.grid_rowconfigure(1, weight=1)
    
    def create_summary_card(self, parent: tk.Frame, title: str, content: str, 
                           colors: dict, row: int, col: int):
        """Crea una tarjeta de resumen individual."""
        # Contenedor de tarjeta con borde
        card_container = tk.Frame(
            parent, 
            bg=colors["red_dark"], 
            padx=2, 
            pady=2
        )
        card_container.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        card_frame = tk.Frame(card_container, bg=colors["bg_dark"], padx=20, pady=20)
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(
            card_frame,
            text=title,
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=colors["red_primary"],
            bg=colors["bg_dark"]
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # Contenido (se actualizará)
        content_label = tk.Label(
            card_frame,
            text=content,
            font=(Settings.FONT_PRIMARY, 10),
            fg=colors["text_secondary"],
            bg=colors["bg_dark"],
            justify=tk.LEFT,
            wraplength=300
        )
        content_label.pack(anchor="w", fill=tk.X)
        
        # Guardar referencia para actualizar
        return {"frame": card_frame, "content_label": content_label}
    
    def create_navigation_bar(self, parent: tk.Frame, colors: dict):
        """Crea la barra de navegación con botones para los módulos."""
        # Frame para la barra de navegación
        nav_frame = tk.Frame(parent, bg=colors["bg_medium"], height=80)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        # Frame interno con padding
        nav_inner = tk.Frame(nav_frame, bg=colors["bg_medium"])
        nav_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Línea superior
        tk.Frame(nav_frame, bg=colors["red_primary"], height=2).pack(fill=tk.X, side=tk.TOP)
        
        # Botones de navegación
        btn_frame = tk.Frame(nav_inner, bg=colors["bg_medium"])
        btn_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botón Inventarios
        btn_inventario = ttk.Button(
            btn_frame,
            text="📦 Inventarios",
            command=self.open_inventory,
            style="Nav.TButton",
            width=20
        )
        btn_inventario.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Botón Ventas
        btn_ventas = ttk.Button(
            btn_frame,
            text="💰 Ventas",
            command=self.open_sales,
            style="Nav.TButton",
            width=20
        )
        btn_ventas.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Botón Cierre de Caja
        btn_cierre = ttk.Button(
            btn_frame,
            text="💵 Cierre de Caja",
            command=self.open_cash_closure,
            style="Nav.TButton",
            width=20
        )
        btn_cierre.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Crear estilo para botones de navegación
        self.style_manager.style.configure(
            "Nav.TButton",
            background=colors["bg_dark"],
            foreground=colors["text_primary"],
            font=(Settings.FONT_PRIMARY, 11, "bold"),
            padding=(15, 10),
            borderwidth=2,
            relief="flat"
        )
        self.style_manager.style.map(
            "Nav.TButton",
            background=[("active", colors["red_primary"]), ("pressed", colors["red_dark"])],
            foreground=[("active", colors["text_primary"])]
        )
    
    def update_summary(self):
        """Actualiza las tarjetas de resumen con datos actuales."""
        # Verificar que las tarjetas estén inicializadas
        if not hasattr(self, 'inventory_card') or not hasattr(self, 'summary_colors'):
            return
        
        data = self.get_summary_data()
        c = self.summary_colors
        
        # Formatear valores monetarios
        def format_currency(value):
            return f"${value:,.2f}".replace(",", ".")
        
        # Actualizar tarjeta de Inventario
        inventory_text = (
            f"Total de Productos: {data['total_productos']}\n"
            f"Valor Total: {format_currency(data['valor_total_inventario'])}\n"
            f"Bajo Stock (<10): {data['productos_bajo_stock']}"
        )
        self.inventory_card["content_label"].config(text=inventory_text)
        
        # Actualizar tarjeta de Ventas
        sales_text = (
            f"Total de Ventas: {data['total_ventas']}\n"
            f"Ingresos Totales: {format_currency(data['total_ingresos'])}"
        )
        self.sales_card["content_label"].config(text=sales_text)
        
        # Actualizar tarjeta de Hoy
        daily_text = (
            f"Ventas Hoy: {data['ventas_hoy']}\n"
            f"Ingresos Hoy: {format_currency(data['ingresos_hoy'])}"
        )
        self.daily_card["content_label"].config(text=daily_text)
        
        # Actualizar tarjeta de Mes
        monthly_text = (
            f"Ventas del Mes: {data['ventas_mes']}\n"
            f"Ingresos del Mes: {format_currency(data['ingresos_mes'])}"
        )
        self.monthly_card["content_label"].config(text=monthly_text)
    
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
        
        # Actualizar resumen después de abrir
        self.root.after(1000, self.update_summary)
    
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
        
        # Actualizar resumen después de abrir
        self.root.after(1000, self.update_summary)
    
    def on_inventory_close(self):
        """Maneja el cierre de la ventana de inventarios."""
        if self.inventory_window:
            self.inventory_window.window.destroy()
            self.inventory_window = None
            # Limpiar referencia en ventas
            if self.sales_window:
                self.sales_window.inventory_gui_ref = None
        # Actualizar resumen
        self.update_summary()
    
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
        
        # Actualizar resumen después de abrir
        self.root.after(1000, self.update_summary)
    
    def on_sales_close(self):
        """Maneja el cierre de la ventana de ventas."""
        if self.sales_window:
            self.sales_window.window.destroy()
            self.sales_window = None
        # Actualizar resumen
        self.update_summary()
    
    def on_cash_closure_close(self):
        """Maneja el cierre de la ventana de cierre de caja."""
        if self.cash_closure_window:
            self.cash_closure_window.window.destroy()
            self.cash_closure_window = None
        # Actualizar resumen
        self.update_summary()
    
    def open_github(self):
        """Abre el repositorio de GitHub en el navegador."""
        webbrowser.open("https://github.com/DevJhojan/Store")


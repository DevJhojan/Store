"""Vista de la interfaz gráfica del módulo de Ventas."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List

from ..config.settings import Settings, COLORS
from ..ui.styles import StyleManager
from ..utils.validators import parse_numeric_field
from .domain.models import Venta, ItemVenta
from .services.venta_service import VentaService


class SalesGUI:
    """Interfaz gráfica del módulo de gestión de ventas."""
    
    def __init__(self, parent_window, service: Optional[VentaService] = None):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            parent_window: Ventana padre (Tk o Toplevel)
            service: Servicio de ventas (si None, se crea uno nuevo)
        """
        self.parent = parent_window
        self.service = service or VentaService()
        
        # Crear ventana Toplevel si el padre es Tk, o usar Frame si es Frame
        if isinstance(parent_window, tk.Tk):
            self.window = tk.Toplevel(parent_window)
            is_frame = False
        elif isinstance(parent_window, tk.Frame):
            self.window = parent_window
            is_frame = True
        else:
            self.window = parent_window
            is_frame = False
        
        # Venta actual en proceso
        self.venta_actual = Venta()
        
        # Configuración de impuestos y descuentos a nivel de venta
        self.impuesto_porcentaje_venta = 0.0  # Porcentaje de impuesto a nivel de venta
        self.descuento_fijo_venta = 0.0  # Descuento fijo a nivel de venta
        self.descuento_porcentaje_venta = 0.0  # Descuento porcentual a nivel de venta
        
        # Inicializar labels de totales (se crearán después)
        self.subtotal_label = None
        self.descuento_label = None
        self.impuesto_label = None
        self.total_label = None
        
        # Referencia al módulo de inventario (para notificaciones)
        self.inventory_gui_ref = None
        
        # Configurar ventana (solo si no es Frame)
        if not is_frame:
            self.window.title("[ Sistema de Gestión de Ventas ]")
            self.window.configure(bg=COLORS["bg_darkest"])
            self.window.resizable(True, True)
            
            # Maximizar la ventana (compatible con todos los sistemas)
            try:
                # Intentar maximizar en Linux
                self.window.attributes('-zoomed', True)
            except:
                try:
                    # Maximizar en Windows
                    self.window.state('zoomed')
                except:
                    # Si nada funciona, obtener tamaño de pantalla y establecer geometría
                    self.window.update_idletasks()
                    width = self.window.winfo_screenwidth()
                    height = self.window.winfo_screenheight()
                    self.window.geometry(f"{width}x{height}")
            
            # Manejar cierre de ventana
            self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        else:
            # Si es Frame, solo configurar el fondo
            self.window.configure(bg=COLORS["bg_darkest"])
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Crear interfaz con scrollbar
        self.create_widgets_with_scroll()
        
        # Cargar productos disponibles
        self.load_available_products()
    
    def create_widgets_with_scroll(self):
        """Crear widgets con scrollbar para contenido grande."""
        c = COLORS
        
        # Canvas principal para scrollbar
        canvas = tk.Canvas(
            self.window,
            bg=c["bg_darkest"],
            highlightthickness=0
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar vertical estilizada
        v_scrollbar = ttk.Scrollbar(
            self.window,
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
        
        # Función para actualizar scroll region
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # Función para hacer scroll con mouse wheel (compatible Windows y Linux)
        def on_main_canvas_mousewheel(event):
            """Maneja el scroll del mouse wheel en el canvas principal."""
            # Windows y Mac
            if hasattr(event, 'delta') and event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Linux
            elif hasattr(event, 'num'):
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        
        # Función para aplicar mouse wheel a todos los widgets de forma recursiva
        def bind_mousewheel_to_all_widgets(parent):
            """Aplica bind de mouse wheel a todos los widgets recursivamente."""
            try:
                # Bind al widget padre
                if not isinstance(parent, (ttk.Treeview, tk.Canvas)):
                    parent.bind("<MouseWheel>", on_main_canvas_mousewheel)
                    parent.bind("<Button-4>", on_main_canvas_mousewheel)
                    parent.bind("<Button-5>", on_main_canvas_mousewheel)
                
                # Aplicar a todos los hijos recursivamente
                for child in parent.winfo_children():
                    # Omitir Treeviews (tienen su propio scroll)
                    if isinstance(child, ttk.Treeview):
                        continue
                    # Bind a este widget
                    child.bind("<MouseWheel>", on_main_canvas_mousewheel)
                    child.bind("<Button-4>", on_main_canvas_mousewheel)
                    child.bind("<Button-5>", on_main_canvas_mousewheel)
                    # Si es un contenedor, aplicar recursivamente
                    if isinstance(child, (tk.Frame, tk.LabelFrame, tk.Toplevel)):
                        bind_mousewheel_to_all_widgets(child)
            except:
                pass  # Ignorar errores si el widget fue destruido
        
        # Bind directo en el canvas
        canvas.bind("<MouseWheel>", on_main_canvas_mousewheel)
        canvas.bind("<Button-4>", on_main_canvas_mousewheel)
        canvas.bind("<Button-5>", on_main_canvas_mousewheel)
        
        # Bind en el scrollable_frame
        scrollable_frame.bind("<MouseWheel>", on_main_canvas_mousewheel)
        scrollable_frame.bind("<Button-4>", on_main_canvas_mousewheel)
        scrollable_frame.bind("<Button-5>", on_main_canvas_mousewheel)
        
        # Función para capturar eventos en toda la ventana del módulo
        def on_window_mousewheel(event):
            """Captura eventos de mouse wheel en toda la ventana del módulo."""
            widget = event.widget
            # Si el widget es un Treeview, no hacer nada (tiene su propio handler)
            if isinstance(widget, ttk.Treeview):
                return
            # Si el evento viene de un widget dentro de la ventana de ventas
            try:
                # Verificar si el widget pertenece a esta ventana
                widget_toplevel = widget.winfo_toplevel()
                if widget_toplevel == self.window:
                    # Aplicar scroll al canvas principal
                    on_main_canvas_mousewheel(event)
            except:
                pass
        
        # Bind en la ventana del módulo como respaldo
        self.window.bind("<MouseWheel>", on_window_mousewheel)
        self.window.bind("<Button-4>", on_window_mousewheel)
        self.window.bind("<Button-5>", on_window_mousewheel)
        
        # Aplicar binds recursivos después de crear todos los widgets
        def apply_all_binds():
            bind_mousewheel_to_all_widgets(scrollable_frame)
        
        # Aplicar después de un pequeño delay para asegurar que todos los widgets estén creados
        self.window.after(300, apply_all_binds)
        
        # Guardar referencia al canvas para uso posterior
        self.main_canvas = canvas
        self.scrollable_frame = scrollable_frame
        self.on_main_canvas_mousewheel = on_main_canvas_mousewheel  # Guardar función para acceso externo
        
        # Ajustar ancho del scrollable_frame al canvas
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Crear widgets en el frame scrollable
        self.create_widgets(scrollable_frame)
        
        # Guardar referencias
        self.canvas = canvas
        self.scrollable_frame = scrollable_frame
        
        # Aplicar tema actual al inicializar
        self.apply_theme()
    
    def create_widgets(self, parent: tk.Frame):
        """Crear todos los widgets de la interfaz."""
        c = COLORS
        
        # Frame principal con padding
        main_frame = tk.Frame(parent, bg=c["bg_darkest"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # ========== ENCABEZADO ==========
        title_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Línea decorativa superior
        tk.Frame(title_frame, bg=c["red_primary"], height=3).pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="[ SISTEMA DE GESTIÓN DE VENTAS ]",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_LARGE, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="[ Registro de Ventas y Actualización de Stock ]",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_muted"],
            bg=c["bg_darkest"]
        )
        subtitle_label.pack(pady=(2, 0))
        
        # Línea decorativa inferior
        tk.Frame(title_frame, bg=c["red_primary"], height=3).pack(fill=tk.X, pady=(10, 0))
        
        # ========== SECCIÓN DE BÚSQUEDA Y SELECCIÓN (ancho completo) ==========
        search_container = tk.Frame(main_frame, bg=c["red_dark"], padx=2, pady=2)
        search_container.pack(fill=tk.X, pady=(0, 15))
        
        search_frame = tk.Frame(search_container, bg=c["bg_dark"], padx=20, pady=15)
        search_frame.pack(fill=tk.X)
        
        self.create_search_section(search_frame)
        
        # ========== SECCIÓN DE CONFIGURACIÓN DE VENTA (debajo, ancho completo) ==========
        config_container = tk.Frame(main_frame, bg=c["red_dark"], padx=2, pady=2)
        config_container.pack(fill=tk.X, pady=(0, 15))
        
        # Frame interno para el contenido de configuración
        config_content_frame = tk.Frame(config_container, bg=c["bg_dark"], padx=20, pady=15)
        config_content_frame.pack(fill=tk.X)
        
        # Frame para formulario (izquierda) y botones (derecha)
        config_form_and_buttons = tk.Frame(config_content_frame, bg=c["bg_dark"])
        config_form_and_buttons.pack(fill=tk.X)
        
        # Frame para el formulario (campos de impuesto y descuentos) - LADO IZQUIERDO
        config_form_frame = tk.Frame(config_form_and_buttons, bg=c["bg_dark"])
        config_form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Frame para los botones - LADO DERECHO
        config_buttons_frame = tk.Frame(config_form_and_buttons, bg=c["bg_dark"])
        config_buttons_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Guardar referencias
        self.config_form_frame = config_form_frame
        self.config_buttons_frame = config_buttons_frame
        
        self.create_config_section(config_form_frame, config_buttons_frame)
        
        # ========== CONTENEDOR PARA CARRITO Y BOTÓN FLOTANTE ==========
        cart_and_actions_container = tk.Frame(main_frame, bg=c["bg_darkest"])
        cart_and_actions_container.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # Frame para el carrito de compra (lado izquierdo)
        cart_container = tk.Frame(cart_and_actions_container, bg=c["red_dark"], padx=2, pady=2)
        cart_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        cart_frame = tk.Frame(cart_container, bg=c["bg_dark"])
        cart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_cart_section(cart_frame)
        
        # Frame para botón flotante (lado derecho)
        floating_actions_frame = tk.Frame(cart_and_actions_container, bg=c["bg_darkest"], width=280)
        floating_actions_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))
        floating_actions_frame.pack_propagate(False)
        
        self.create_floating_button_section(floating_actions_frame)
    
    def create_search_section(self, parent: tk.Frame):
        """Crear la sección de búsqueda y selección de productos."""
        c = COLORS
        
        # Título de sección
        tk.Label(
            parent,
            text="► AGREGAR PRODUCTO A LA VENTA",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"]
        ).pack(anchor="w", pady=(0, 10))
        
        # Frame para búsqueda
        search_row = tk.Frame(parent, bg=c["bg_dark"])
        search_row.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            search_row,
            text="Código:",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["text_primary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.codigo_entry = tk.Entry(
            search_row,
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            bg=c["bg_darkest"],
            fg=c["text_primary"],
            insertbackground=c["red_primary"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=c["red_dark"],
            highlightcolor=c["red_bright"],
            width=15
        )
        self.codigo_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.codigo_entry.bind("<Return>", lambda e: self.buscar_producto())
        
        btn_buscar = ttk.Button(
            search_row,
            text="[ Buscar ]",
            command=self.buscar_producto,
            style="Secondary.TButton"
        )
        btn_buscar.pack(side=tk.LEFT, padx=(0, 20))
        
        # Búsqueda por nombre (nueva fila)
        search_name_row = tk.Frame(parent, bg=c["bg_dark"])
        search_name_row.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(
            search_name_row,
            text="Buscar por Nombre:",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["text_primary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.nombre_buscar_entry = tk.Entry(
            search_name_row,
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            bg=c["bg_darkest"],
            fg=c["text_primary"],
            insertbackground=c["red_primary"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=c["red_dark"],
            highlightcolor=c["red_bright"],
            width=30
        )
        self.nombre_buscar_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.nombre_buscar_entry.bind("<Return>", lambda e: self.buscar_por_nombre())
        self.nombre_buscar_entry.bind("<KeyRelease>", lambda e: self.buscar_por_nombre_auto())
        
        btn_buscar_nombre = ttk.Button(
            search_name_row,
            text="[ Buscar Nombre ]",
            command=self.buscar_por_nombre,
            style="Secondary.TButton"
        )
        btn_buscar_nombre.pack(side=tk.LEFT, padx=(0, 20))
        
        # Combo para selección rápida de productos encontrados
        tk.Label(
            search_name_row,
            text="Resultados:",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.product_combo = ttk.Combobox(
            search_name_row,
            state="readonly",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            width=30
        )
        self.product_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.product_combo.bind("<<ComboboxSelected>>", self.on_product_selected)
        
        # Lista de productos encontrados por nombre
        self.productos_encontrados = []
        
        # Información del producto seleccionado
        self.product_info_frame = tk.Frame(parent, bg=c["bg_dark"])
        self.product_info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Campos para cantidad
        qty_row = tk.Frame(parent, bg=c["bg_dark"])
        qty_row.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            qty_row,
            text="Cantidad:",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["text_primary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.cantidad_entry = tk.Entry(
            qty_row,
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            bg=c["bg_darkest"],
            fg=c["text_primary"],
            insertbackground=c["red_primary"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=c["red_dark"],
            highlightcolor=c["red_bright"],
            width=10
        )
        self.cantidad_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.cantidad_entry.insert(0, "1")
        
        btn_agregar = ttk.Button(
            qty_row,
            text="[ + ] Agregar al Carrito",
            command=self.agregar_al_carrito,
            style="Accent.TButton"
        )
        btn_agregar.pack(side=tk.LEFT)
        
        # Variable para producto seleccionado
        self.producto_seleccionado = None
    
    def create_config_section(self, form_parent: tk.Frame, buttons_parent: tk.Frame):
        """Crear el panel de configuración (impuestos y descuentos) con formulario y botones separados."""
        c = COLORS
        
        # Título (en el frame del formulario)
        tk.Label(
            form_parent,
            text="► CONFIGURACIÓN DE VENTA",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"]
        ).pack(anchor="w", pady=(0, 15))
        
        # ========== IMPUESTOS ==========
        impuesto_frame = tk.Frame(form_parent, bg=c["bg_dark"])
        impuesto_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        tk.Label(
            impuesto_frame,
            text="Impuesto (%):",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["text_primary"],
            bg=c["bg_dark"]
        ).pack(anchor="w", pady=(0, 5))
        
        impuesto_entry_frame = tk.Frame(impuesto_frame, bg=c["bg_dark"])
        impuesto_entry_frame.pack(fill=tk.X)
        
        self.impuesto_entry = tk.Entry(
            impuesto_entry_frame,
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            bg=c["bg_darkest"],
            fg=c["text_primary"],
            insertbackground=c["red_primary"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=c["red_dark"],
            highlightcolor=c["red_bright"],
            width=15
        )
        self.impuesto_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.impuesto_entry.insert(0, "0")
        self.impuesto_entry.bind("<KeyRelease>", lambda e: self.actualizar_totales())
        
        tk.Label(
            impuesto_entry_frame,
            text="%",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT)
        
        # ========== DESCUENTOS ==========
        descuento_frame = tk.Frame(form_parent, bg=c["bg_dark"])
        descuento_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        tk.Label(
            descuento_frame,
            text="Descuento Fijo ($):",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["text_primary"],
            bg=c["bg_dark"]
        ).pack(anchor="w", pady=(0, 5))
        
        self.descuento_fijo_entry = tk.Entry(
            descuento_frame,
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            bg=c["bg_darkest"],
            fg=c["text_primary"],
            insertbackground=c["red_primary"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=c["red_dark"],
            highlightcolor=c["red_bright"],
            width=15
        )
        self.descuento_fijo_entry.pack(anchor="w", pady=(0, 10))
        self.descuento_fijo_entry.insert(0, "0")
        self.descuento_fijo_entry.bind("<KeyRelease>", lambda e: self.actualizar_totales())
        
        tk.Label(
            descuento_frame,
            text="Descuento Porcentual (%):",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["text_primary"],
            bg=c["bg_dark"]
        ).pack(anchor="w", pady=(0, 5))
        
        descuento_pct_frame = tk.Frame(descuento_frame, bg=c["bg_dark"])
        descuento_pct_frame.pack(fill=tk.X)
        
        self.descuento_porcentaje_entry = tk.Entry(
            descuento_pct_frame,
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            bg=c["bg_darkest"],
            fg=c["text_primary"],
            insertbackground=c["red_primary"],
            relief="flat",
            highlightthickness=2,
            highlightbackground=c["red_dark"],
            highlightcolor=c["red_bright"],
            width=15
        )
        self.descuento_porcentaje_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.descuento_porcentaje_entry.insert(0, "0")
        self.descuento_porcentaje_entry.bind("<KeyRelease>", lambda e: self.actualizar_totales())
        
        tk.Label(
            descuento_pct_frame,
            text="%",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT)
        
        # ========== BOTONES (LADO DERECHO) ==========
        # Botón aplicar - PRINCIPAL (más grande y destacado)
        btn_aplicar = ttk.Button(
            buttons_parent,
            text="✅ APLICAR\nCONFIGURACIÓN",
            command=self.aplicar_configuracion,
            style="Accent.TButton",
            width=20
        )
        btn_aplicar.pack(pady=(0, 10), ipady=15, ipadx=10)
        
        # Botón limpiar
        btn_limpiar_config = ttk.Button(
            buttons_parent,
            text="[ Limpiar Configuración ]",
            command=self.limpiar_configuracion,
            style="Secondary.TButton",
            width=20
        )
        btn_limpiar_config.pack(ipady=12, ipadx=10)
        
        # Guardar referencia al botón para verificación
        self.btn_aplicar_config = btn_aplicar
    
    def create_cart_section(self, parent: tk.Frame):
        """Crear la sección del carrito de compra."""
        c = COLORS
        
        # Título
        title_label = tk.Label(
            parent,
            text="► CARRITO DE COMPRA",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"]
        )
        title_label.pack(anchor="w", padx=5, pady=5)
        
        # Frame para tabla con scrollbar
        table_container = tk.Frame(parent, bg=c["bg_dark"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar vertical para la tabla
        table_scrollbar = ttk.Scrollbar(
            table_container,
            style="Custom.Vertical.TScrollbar"
        )
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para items
        columns = ("codigo", "nombre", "cantidad", "precio", "subtotal")
        self.cart_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=table_scrollbar.set
        )
        
        headings = {
            "codigo": "Código",
            "nombre": "Producto",
            "cantidad": "Cantidad",
            "precio": "P. Unitario",
            "subtotal": "Subtotal"
        }
        
        widths = {"codigo": 100, "nombre": 250, "cantidad": 80, "precio": 100, "subtotal": 100}
        
        for col in columns:
            self.cart_tree.heading(col, text=headings[col])
            self.cart_tree.column(col, width=widths[col], anchor="center")
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        table_scrollbar.config(command=self.cart_tree.yview)
        
        # Función para hacer scroll con mouse wheel en la tabla (compatible Windows y Linux)
        def on_treeview_mousewheel(event):
            """Maneja el scroll del mouse wheel sobre la tabla del carrito."""
            # Windows y Mac
            if event.delta:
                self.cart_tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Linux
            elif event.num == 4:
                self.cart_tree.yview_scroll(-1, "units")
            elif event.num == 5:
                self.cart_tree.yview_scroll(1, "units")
        
        # Bind para mouse wheel en la tabla del carrito
        self.cart_tree.bind("<MouseWheel>", on_treeview_mousewheel)
        self.cart_tree.bind("<Button-4>", on_treeview_mousewheel)
        self.cart_tree.bind("<Button-5>", on_treeview_mousewheel)
        
        # También bind en el contenedor de la tabla
        table_container.bind("<MouseWheel>", lambda e: on_treeview_mousewheel(e))
        table_container.bind("<Button-4>", lambda e: on_treeview_mousewheel(e))
        table_container.bind("<Button-5>", lambda e: on_treeview_mousewheel(e))
        
        # Botón para remover item
        btn_remover = ttk.Button(
            parent,
            text="[ X ] Remover Item Seleccionado",
            command=self.remover_item,
            style="Secondary.TButton"
        )
        btn_remover.pack(anchor="w", padx=5, pady=5)
    
    def create_floating_button_section(self, parent: tk.Frame):
        """Crea la sección de botón flotante al lado derecho del carrito."""
        c = COLORS
        
        # Frame contenedor del botón flotante con borde
        floating_container = tk.Frame(parent, bg=c["red_primary"], padx=3, pady=3)
        floating_container.pack(side=tk.TOP, pady=(0, 15))
        
        floating_inner = tk.Frame(floating_container, bg=c["bg_dark"], padx=25, pady=30)
        floating_inner.pack(fill=tk.BOTH)
        
        # Frame para totales detallados
        total_frame = tk.Frame(floating_inner, bg=c["red_dark"], padx=2, pady=2)
        total_frame.pack(fill=tk.X, pady=(0, 20))
        
        total_inner = tk.Frame(total_frame, bg=c["bg_darkest"], padx=15, pady=15)
        total_inner.pack(fill=tk.BOTH)
        
        # Labels para mostrar totales
        self.subtotal_label = tk.Label(
            total_inner,
            text="Subtotal: $0.00",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_secondary"],
            bg=c["bg_darkest"],
            anchor="w"
        )
        self.subtotal_label.pack(fill=tk.X, pady=(0, 3))
        
        self.descuento_label = tk.Label(
            total_inner,
            text="Descuento: $0.00",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_secondary"],
            bg=c["bg_darkest"],
            anchor="w"
        )
        self.descuento_label.pack(fill=tk.X, pady=(0, 3))
        
        self.impuesto_label = tk.Label(
            total_inner,
            text="Impuestos: $0.00",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_secondary"],
            bg=c["bg_darkest"],
            anchor="w"
        )
        self.impuesto_label.pack(fill=tk.X, pady=(0, 8))
        
        # Línea separadora
        tk.Frame(total_inner, bg=c["bg_medium"], height=1).pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(
            total_inner,
            text="TOTAL",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"],
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 3))
        
        self.total_label = tk.Label(
            total_inner,
            text="$0.00",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_LARGE, "bold"),
            fg=c["success"],
            bg=c["bg_darkest"]
        )
        self.total_label.pack(fill=tk.X)
        
        # Botón principal de Registrar Venta (flotante, grande)
        btn_registrar = ttk.Button(
            floating_inner,
            text="[ REGISTRAR VENTA ]",
            command=self.registrar_venta,
            style="Accent.TButton"
        )
        btn_registrar.pack(fill=tk.X, pady=(0, 15), ipady=12)
        
        # Botón secundario
        btn_limpiar = ttk.Button(
            floating_inner,
            text="[ Nueva Venta ]",
            command=self.nueva_venta,
            style="Secondary.TButton"
        )
        btn_limpiar.pack(fill=tk.X, ipady=8)
    
    def load_available_products(self):
        """Cargar productos disponibles en el combo."""
        productos = self.service.obtener_productos_disponibles()
        productos_texto = [f"{p.codigo} - {p.nombre} (Stock: {p.cantidad})" for p in productos]
        self.product_combo["values"] = productos_texto
        self.productos_disponibles = {p.codigo: p for p in productos}
    
    def buscar_por_nombre(self):
        """Busca productos por nombre y muestra resultados."""
        nombre = self.nombre_buscar_entry.get().strip()
        if not nombre:
            messagebox.showwarning(
                "Advertencia",
                "Ingrese un nombre para buscar.",
                parent=self.window
            )
            return
        
        productos = self.service.buscar_productos_por_nombre(nombre)
        self.productos_encontrados = productos
        
        if not productos:
            messagebox.showinfo(
                "Búsqueda",
                f"No se encontraron productos con el nombre '{nombre}'.",
                parent=self.window
            )
            self.product_combo["values"] = []
            return
        
        # Actualizar combo con resultados
        productos_texto = [f"{p.codigo} - {p.nombre} (Stock: {p.cantidad})" for p in productos]
        self.product_combo["values"] = productos_texto
        self.productos_disponibles = {p.codigo: p for p in productos}
        
        if len(productos) == 1:
            # Si solo hay un resultado, seleccionarlo automáticamente
            self.product_combo.set(productos_texto[0])
            self.on_product_selected()
    
    def buscar_por_nombre_auto(self):
        """Búsqueda automática mientras se escribe (sin mostrar mensajes)."""
        nombre = self.nombre_buscar_entry.get().strip()
        if len(nombre) >= 2:  # Solo buscar si hay al menos 2 caracteres
            productos = self.service.buscar_productos_por_nombre(nombre)
            self.productos_encontrados = productos
            if productos:
                productos_texto = [f"{p.codigo} - {p.nombre} (Stock: {p.cantidad})" for p in productos]
                self.product_combo["values"] = productos_texto
                self.productos_disponibles = {p.codigo: p for p in productos}
    
    def aplicar_configuracion(self):
        """Aplica la configuración de impuestos y descuentos."""
        # Leer valores de impuesto
        try:
            impuesto_val = self.impuesto_entry.get().strip()
            if impuesto_val:
                impuesto_val = float(impuesto_val)
                # Si es mayor que 1, asumir que es porcentaje directo (ej: 19)
                # Si es menor que 1, asumir que es decimal (ej: 0.19)
                if impuesto_val > 1:
                    self.impuesto_porcentaje_venta = impuesto_val / 100.0
                else:
                    self.impuesto_porcentaje_venta = impuesto_val
            else:
                self.impuesto_porcentaje_venta = 0.0
        except ValueError:
            messagebox.showerror(
                "Error",
                "El valor de impuesto debe ser un número.",
                parent=self.window
            )
            return
        
        # Leer descuento fijo
        try:
            desc_fijo_val = self.descuento_fijo_entry.get().strip()
            self.descuento_fijo_venta = float(desc_fijo_val) if desc_fijo_val else 0.0
        except ValueError:
            messagebox.showerror(
                "Error",
                "El descuento fijo debe ser un número.",
                parent=self.window
            )
            return
        
        # Leer descuento porcentual
        try:
            desc_pct_val = self.descuento_porcentaje_entry.get().strip()
            if desc_pct_val:
                desc_pct_val = float(desc_pct_val)
                # Si es mayor que 1, asumir que es porcentaje directo
                if desc_pct_val > 1:
                    self.descuento_porcentaje_venta = desc_pct_val / 100.0
                else:
                    self.descuento_porcentaje_venta = desc_pct_val
            else:
                self.descuento_porcentaje_venta = 0.0
        except ValueError:
            messagebox.showerror(
                "Error",
                "El descuento porcentual debe ser un número.",
                parent=self.window
            )
            return
        
        # Actualizar totales
        self.actualizar_totales()
        
        messagebox.showinfo(
            "Configuración",
            "Configuración aplicada correctamente.",
            parent=self.window
        )
    
    def limpiar_configuracion(self):
        """Limpia la configuración de impuestos y descuentos."""
        self.impuesto_entry.delete(0, tk.END)
        self.impuesto_entry.insert(0, "0")
        self.descuento_fijo_entry.delete(0, tk.END)
        self.descuento_fijo_entry.insert(0, "0")
        self.descuento_porcentaje_entry.delete(0, tk.END)
        self.descuento_porcentaje_entry.insert(0, "0")
        
        self.impuesto_porcentaje_venta = 0.0
        self.descuento_fijo_venta = 0.0
        self.descuento_porcentaje_venta = 0.0
        
        self.actualizar_totales()
    
    def on_product_selected(self, event=None):
        """Maneja la selección de producto del combo."""
        selection = self.product_combo.get()
        if selection:
            codigo = selection.split(" - ")[0]
            self.codigo_entry.delete(0, tk.END)
            self.codigo_entry.insert(0, codigo)
            self.buscar_producto()
    
    def buscar_producto(self):
        """Busca un producto por código y muestra su información."""
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showwarning(
                "Advertencia",
                "Ingrese un código de producto.",
                parent=self.window
            )
            return
        
        producto = self.service.buscar_producto_por_codigo(codigo)
        if not producto:
            messagebox.showerror(
                "Error",
                f"Producto con código '{codigo}' no encontrado.",
                parent=self.window
            )
            self.limpiar_info_producto()
            return
        
        if producto.cantidad == 0:
            messagebox.showwarning(
                "Advertencia",
                f"El producto '{producto.nombre}' no tiene stock disponible.",
                parent=self.window
            )
            self.limpiar_info_producto()
            return
        
        self.producto_seleccionado = producto
        self.mostrar_info_producto(producto)
        self.cantidad_entry.focus()
    
    def mostrar_info_producto(self, producto):
        """Muestra la información del producto seleccionado."""
        c = COLORS
        
        # Limpiar frame anterior
        for widget in self.product_info_frame.winfo_children():
            widget.destroy()
        
        # Asegurar que valor_venta esté calculado
        if producto.valor_venta == 0.0:
            producto.valor_venta = producto.calcular_valor_venta()
        
        info_text = (
            f"Nombre: {producto.nombre} | "
            f"Categoría: {producto.categoria} | "
            f"Valor de Venta: ${producto.valor_venta:.2f} | "
            f"Stock disponible: {producto.cantidad}"
        )
        
        tk.Label(
            self.product_info_frame,
            text=info_text,
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_primary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT)
    
    def limpiar_info_producto(self):
        """Limpiar la información del producto."""
        for widget in self.product_info_frame.winfo_children():
            widget.destroy()
        self.producto_seleccionado = None
    
    def agregar_al_carrito(self):
        """Agrega el producto actual al carrito."""
        if not self.producto_seleccionado:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un producto primero.",
                parent=self.window
            )
            return
        
        # Validar cantidad
        cantidad_exitoso, cantidad, msg_cantidad = parse_numeric_field(
            self.cantidad_entry.get().strip(), int
        )
        if not cantidad_exitoso:
            messagebox.showerror(
                "Error",
                f"Cantidad: {msg_cantidad}",
                parent=self.window
            )
            return
        
        if cantidad <= 0:
            messagebox.showerror(
                "Error",
                "La cantidad debe ser mayor a 0.",
                parent=self.window
            )
            return
        
        # Verificar stock disponible
        if cantidad > self.producto_seleccionado.cantidad:
            messagebox.showerror(
                "Error",
                f"Stock insuficiente. Disponible: {self.producto_seleccionado.cantidad}, "
                f"Solicitado: {cantidad}.",
                parent=self.window
            )
            return
        
        # Verificar si ya está en el carrito
        for item in self.venta_actual.items:
            if item.codigo_producto == self.producto_seleccionado.codigo:
                nueva_cantidad_total = item.cantidad + cantidad
                if nueva_cantidad_total > self.producto_seleccionado.cantidad:
                    messagebox.showerror(
                        "Error",
                        f"La cantidad total ({nueva_cantidad_total}) excede el stock disponible "
                        f"({self.producto_seleccionado.cantidad}).",
                        parent=self.window
                    )
                    return
                item.cantidad = nueva_cantidad_total
                self.actualizar_carrito()
                return
        
        # Asegurar que valor_venta esté calculado
        if self.producto_seleccionado.valor_venta == 0.0:
            self.producto_seleccionado.valor_venta = self.producto_seleccionado.calcular_valor_venta()
        
        # Agregar nuevo item usando valor_venta (no precio_unitario)
        item = ItemVenta(
            codigo_producto=self.producto_seleccionado.codigo,
            nombre_producto=self.producto_seleccionado.nombre,
            cantidad=cantidad,
            precio_unitario=self.producto_seleccionado.valor_venta
        )
        
        self.venta_actual.agregar_item(item)
        self.actualizar_carrito()
        
        # Limpiar campos
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "1")
        self.limpiar_info_producto()
        self.codigo_entry.delete(0, tk.END)
        self.codigo_entry.focus()
    
    def actualizar_carrito(self):
        """Actualiza la visualización del carrito."""
        # Limpiar tabla
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Agregar items
        for item in self.venta_actual.items:
            self.cart_tree.insert("", tk.END, values=(
                item.codigo_producto,
                item.nombre_producto,
                item.cantidad,
                f"${item.precio_unitario:.2f}",
                f"${item.calcular_subtotal():.2f}"
            ))
        
        # Actualizar totales con impuestos y descuentos
        self.actualizar_totales()
    
    def actualizar_totales(self):
        """Recalcula y actualiza todos los totales incluyendo impuestos y descuentos a nivel de venta."""
        # Calcular subtotal desde items
        subtotal_items = sum(item.calcular_subtotal() for item in self.venta_actual.items)
        descuento_items = sum(item.calcular_descuento() for item in self.venta_actual.items)
        
        # Aplicar descuentos a nivel de venta
        subtotal_con_descuento_items = subtotal_items - descuento_items
        
        # Descuento fijo
        descuento_fijo_aplicado = self.descuento_fijo_venta
        
        # Descuento porcentual sobre el subtotal con descuento de items
        descuento_porcentual_aplicado = subtotal_con_descuento_items * self.descuento_porcentaje_venta
        
        # Subtotal después de todos los descuentos
        subtotal_final = subtotal_con_descuento_items - descuento_fijo_aplicado - descuento_porcentual_aplicado
        if subtotal_final < 0:
            subtotal_final = 0.0
        
        # Calcular impuesto sobre el subtotal final
        impuesto_aplicado = subtotal_final * self.impuesto_porcentaje_venta
        impuesto_items = sum(item.calcular_impuesto() for item in self.venta_actual.items)
        
        # Total final
        total_final = subtotal_final + impuesto_aplicado + impuesto_items
        
        # Actualizar modelo de venta
        self.venta_actual.subtotal = subtotal_items
        self.venta_actual.descuento_total = descuento_items + descuento_fijo_aplicado + descuento_porcentual_aplicado
        self.venta_actual.impuesto_total = impuesto_items + impuesto_aplicado
        self.venta_actual.total = total_final
        
        # Actualizar todos los labels de totales (solo si están inicializados)
        if self.subtotal_label:
            self.subtotal_label.config(text=f"Subtotal: ${subtotal_items:,.2f}")
        if self.descuento_label:
            self.descuento_label.config(text=f"Descuento: ${self.venta_actual.descuento_total:,.2f}")
        if self.impuesto_label:
            self.impuesto_label.config(text=f"Impuestos: ${self.venta_actual.impuesto_total:,.2f}")
        if self.total_label:
            self.total_label.config(text=f"${total_final:,.2f}")
    
    def remover_item(self):
        """Remueve el item seleccionado del carrito."""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un item para remover.",
                parent=self.window
            )
            return
        
        index = self.cart_tree.index(selected[0])
        self.venta_actual.remover_item(index)
        self.actualizar_carrito()
    
    def registrar_venta(self):
        """Registra la venta, actualiza inventario y genera PDF."""
        if not self.venta_actual.items:
            messagebox.showwarning(
                "Advertencia",
                "El carrito está vacío.",
                parent=self.window
            )
            return
        
        # Actualizar totales ANTES de confirmar y registrar (incluye descuentos e impuestos configurados)
        self.actualizar_totales()
        
        # Confirmar venta
        total = self.venta_actual.total
        if not messagebox.askyesno(
            "Confirmar Venta",
            f"¿Confirmar venta por un total de ${total:,.2f}?",
            parent=self.window
        ):
            return
        
        # Registrar venta (ya tiene los totales actualizados con descuentos e impuestos)
        exitoso, mensaje, venta_id = self.service.registrar_venta(self.venta_actual)
        
        if exitoso:
            # Usar la venta actual que ya tiene los totales correctos (con descuentos e impuestos)
            # No es necesario recuperarla de la BD ya que los valores ya están actualizados
            # Solo asegurar que tenga el ID correcto
            self.venta_actual.id = venta_id
            
            # Generar PDF de factura usando la venta actual con totales correctos
            pdf_path = None
            try:
                from .pdf_generator import generar_factura_pdf
                pdf_path = generar_factura_pdf(self.venta_actual, venta_id)
            except ImportError as e:
                messagebox.showwarning(
                    "Advertencia",
                    f"{mensaje}\nID de Venta: {venta_id}\n\n"
                    f"reportlab no está instalado. Para generar PDFs, instale:\n"
                    f"pip install reportlab\n\n"
                    f"La venta fue registrada correctamente.",
                    parent=self.window
                )
            except Exception as e:
                messagebox.showwarning(
                    "Advertencia",
                    f"{mensaje}\nID de Venta: {venta_id}\n\n"
                    f"Error al generar PDF: {str(e)}\n"
                    f"La venta fue registrada correctamente.",
                    parent=self.window
                )
            
            # Si se generó el PDF, preguntar si desea abrirlo
            if pdf_path:
                if messagebox.askyesno(
                    "Factura Generada",
                    f"{mensaje}\n\n"
                    f"ID de Venta: {venta_id}\n"
                    f"Número de Factura: {self.venta_actual.numero_factura}\n"
                    f"Total: ${self.venta_actual.total:,.2f}\n\n"
                    f"Factura guardada en:\n{pdf_path}\n\n"
                    f"¿Desea abrir la factura ahora?",
                    parent=self.window
                ):
                    import os
                    import subprocess
                    import platform
                    try:
                        if platform.system() == 'Linux':
                            subprocess.run(['xdg-open', pdf_path], check=False)
                        elif platform.system() == 'Windows':
                            os.startfile(pdf_path)
                        elif platform.system() == 'Darwin':
                            subprocess.run(['open', pdf_path], check=False)
                    except Exception:
                        pass  # Si no se puede abrir, no es crítico
            else:
                # Mostrar mensaje de éxito sin PDF
                messagebox.showinfo(
                    "Venta Registrada",
                    f"{mensaje}\n\n"
                    f"ID de Venta: {venta_id}\n"
                    f"Número de Factura: {self.venta_actual.numero_factura}\n"
                    f"Total: ${self.venta_actual.total:,.2f}",
                    parent=self.window
                )
            
            self.nueva_venta()
            # Recargar productos disponibles (stock actualizado)
            self.load_available_products()
            # Notificar al módulo de inventario si está abierto
            if self.inventory_gui_ref:
                self.inventory_gui_ref.refresh()
        else:
            messagebox.showerror(
                "Error",
                mensaje,
                parent=self.window
            )
    
    def finalizar_venta(self):
        """Alias para mantener compatibilidad."""
        self.registrar_venta()
    
    def nueva_venta(self):
        """Inicia una nueva venta (limpia el carrito)."""
        if self.venta_actual.items:
            if not messagebox.askyesno(
                "Confirmar",
                "¿Desea cancelar la venta actual?",
                parent=self.window
            ):
                return
        
        self.venta_actual = Venta()
        self.limpiar_configuracion()
        self.actualizar_carrito()
        self.limpiar_info_producto()
        self.codigo_entry.delete(0, tk.END)
        self.nombre_buscar_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "1")
        self.product_combo.set("")
        self.productos_encontrados = []
        self.load_available_products()
    
    def apply_theme(self):
        """Aplica el tema actual a todos los widgets del módulo."""
        from ..config_module.utils.theme_updater import update_application_theme
        from ..config.settings import COLORS
        
        # Recargar StyleManager con el tema actual
        self.style_manager = StyleManager()
        
        # Actualizar todos los widgets del módulo
        update_application_theme(self.window, self.style_manager)
        
        # Actualizar manualmente el estilo del Combobox de productos si existe
        if hasattr(self, 'product_combo') and self.product_combo:
            try:
                from tkinter import ttk
                style = ttk.Style()
                style.configure("TCombobox", fieldbackground=COLORS["bg_medium"], foreground=COLORS["text_primary"])
            except:
                pass
    
    def on_close(self):
        """Maneja el cierre de la ventana."""
        if self.venta_actual.items:
            if not messagebox.askyesno(
                "Confirmar",
                "Tiene items en el carrito. ¿Desea cancelar la venta?",
                parent=self.window
            ):
                return
        self.window.destroy()

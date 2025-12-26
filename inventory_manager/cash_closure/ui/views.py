"""Vista de la interfaz gráfica del módulo de Cierre de Caja."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from datetime import date, time, datetime

from ...config.settings import Settings, COLORS
from ...ui.styles import StyleManager
from ..services.cash_closure_service import CashClosureService


class CashClosureGUI:
    """Interfaz gráfica del módulo de Cierre de Caja."""
    
    def __init__(self, parent_window, service: Optional[CashClosureService] = None):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            parent_window: Ventana padre (Tk o Toplevel)
            service: Servicio de cierre de caja (si None, se crea uno nuevo)
        """
        self.parent = parent_window
        self.service = service or CashClosureService()
        
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
        
        # Configurar ventana (solo si no es Frame)
        if not is_frame:
            self.window.title("💵 Cierre de Caja")
            self.window.configure(bg=COLORS["bg_darkest"])
            self.window.resizable(True, True)
            
            # Maximizar la ventana
            try:
                self.window.attributes('-zoomed', True)
            except:
                try:
                    self.window.state('zoomed')
                except:
                    self.window.update_idletasks()
                    width = self.window.winfo_screenwidth()
                    height = self.window.winfo_screenheight()
                    self.window.geometry(f"{width}x{height}")
        else:
            # Si es Frame, solo configurar el fondo
            self.window.configure(bg=COLORS["bg_darkest"])
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Variables para filtros
        self.fecha_dia_var = tk.StringVar()
        self.fecha_inicio_var = tk.StringVar()
        self.fecha_fin_var = tk.StringVar()
        self.mes_var = tk.StringVar(value="")
        self.año_var = tk.StringVar(value="")
        self.hora_inicio_var = tk.StringVar()
        self.hora_fin_var = tk.StringVar()
        
        # Variables para detalles de venta
        self.venta_expandida_id = None  # ID de la venta actualmente expandida
        self.detalle_frame = None  # Frame del detalle desplegable
        self.ventas_dict = {}  # Diccionario para mapear items del tree a IDs de venta
        
        # Crear interfaz con scroll
        self.create_widgets_with_scroll()
        
        # Cargar todas las ventas inicialmente
        self.aplicar_filtros()
    
    def create_widgets_with_scroll(self):
        """Crea todos los widgets de la interfaz con scrollbar."""
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
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        # Habilitar scroll con rueda del mouse (Linux)
        def on_button4(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(-1, "units")
            except tk.TclError:
                pass
        
        def on_button5(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(1, "units")
            except tk.TclError:
                pass
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_button4)
        canvas.bind_all("<Button-5>", on_button5)
        
        # Guardar referencia al canvas
        self.canvas = canvas
        
        # Frame principal dentro del scrollable
        main_frame = scrollable_frame
        
        # Padding del frame principal
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="💵 CIERRE DE CAJA",
            font=(Settings.FONT_PRIMARY, 18, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"],
            pady=10
        )
        title_label.pack()
        
        # Frame de filtros
        filters_frame = tk.Frame(main_frame, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
        filters_frame.pack(fill=tk.X, pady=(0, 15))
        
        filters_title = tk.Label(
            filters_frame,
            text="Filtros de Búsqueda",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            pady=10
        )
        filters_title.pack()
        
        # Contenedor de filtros usando grid para mejor distribución
        filters_content = tk.Frame(filters_frame, bg=c["bg_dark"])
        filters_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Configurar columnas del grid para mejor distribución
        filters_content.grid_columnconfigure(1, weight=1)  # Columna de inputs principal (expande)
        filters_content.grid_columnconfigure(2, weight=1)  # Columna para inputs secundarios
        filters_content.grid_columnconfigure(3, weight=2)  # Columna de año con más peso para que sea más ancho
        
        row = 0
        
        # Fila 1: Filtro por día (input ocupa TODO el ancho disponible)
        tk.Label(
            filters_content,
            text="Día específico:",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        
        fecha_dia_entry = tk.Entry(
            filters_content,
            textvariable=self.fecha_dia_var,
            font=(Settings.FONT_PRIMARY, 10),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT
        )
        fecha_dia_entry.grid(row=row, column=1, columnspan=3, sticky="ew", padx=(0, 10), pady=5)
        
        tk.Label(
            filters_content,
            text="(YYYY-MM-DD)",
            font=(Settings.FONT_PRIMARY, 8),
            fg=c["text_muted"],
            bg=c["bg_dark"]
        ).grid(row=row, column=4, sticky="w", pady=5)
        
        row += 1
        
        # Fila 2: Filtro por mes y año (año es más ancho)
        tk.Label(
            filters_content,
            text="Mes:",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        
        mes_combo = ttk.Combobox(
            filters_content,
            textvariable=self.mes_var,
            values=["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
            state="readonly",
            width=8
        )
        mes_combo.grid(row=row, column=1, sticky="w", padx=(0, 15), pady=5)
        
        tk.Label(
            filters_content,
            text="Año:",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).grid(row=row, column=2, sticky="w", padx=(0, 10), pady=5)
        
        año_entry = tk.Entry(
            filters_content,
            textvariable=self.año_var,
            font=(Settings.FONT_PRIMARY, 10),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT
        )
        año_entry.grid(row=row, column=3, sticky="ew", pady=5)
        
        row += 1
        
        # Fila 3: Filtro por rango de horas (inputs ocupan la mitad del espacio disponible)
        tk.Label(
            filters_content,
            text="Rango de horas:",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
        
        # Contenedor para "Desde" (ocupa la mitad del espacio)
        desde_frame = tk.Frame(filters_content, bg=c["bg_dark"])
        desde_frame.grid(row=row, column=1, sticky="ew", pady=5)
        desde_frame.grid_columnconfigure(1, weight=1)  # El input se expande
        
        tk.Label(
            desde_frame,
            text="Desde:",
            font=(Settings.FONT_PRIMARY, 9),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        hora_inicio_entry = tk.Entry(
            desde_frame,
            textvariable=self.hora_inicio_var,
            font=(Settings.FONT_PRIMARY, 10),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT
        )
        hora_inicio_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        tk.Label(
            desde_frame,
            text="(HH:MM)",
            font=(Settings.FONT_PRIMARY, 8),
            fg=c["text_muted"],
            bg=c["bg_dark"]
        ).grid(row=0, column=2, sticky="w", padx=(0, 15))
        
        # Contenedor para "Hasta" (ocupa la mitad del espacio)
        hasta_frame = tk.Frame(filters_content, bg=c["bg_dark"])
        hasta_frame.grid(row=row, column=2, sticky="ew", pady=5)
        hasta_frame.grid_columnconfigure(1, weight=1)  # El input se expande
        
        tk.Label(
            hasta_frame,
            text="Hasta:",
            font=(Settings.FONT_PRIMARY, 9),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        hora_fin_entry = tk.Entry(
            hasta_frame,
            textvariable=self.hora_fin_var,
            font=(Settings.FONT_PRIMARY, 10),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT
        )
        hora_fin_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        tk.Label(
            hasta_frame,
            text="(HH:MM)",
            font=(Settings.FONT_PRIMARY, 8),
            fg=c["text_muted"],
            bg=c["bg_dark"]
        ).grid(row=0, column=2, sticky="w")
        
        row += 1
        
        # Botones de filtro (botón limpiar es más ancho)
        buttons_frame = tk.Frame(filters_content, bg=c["bg_dark"])
        buttons_frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        buttons_frame.grid_columnconfigure(0, weight=1)  # Primer botón
        buttons_frame.grid_columnconfigure(1, weight=2)  # Segundo botón más ancho (doble peso)
        
        btn_aplicar = ttk.Button(
            buttons_frame,
            text="🔍 Aplicar Filtros",
            command=self.aplicar_filtros,
            style="Accent.TButton"
        )
        btn_aplicar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        btn_limpiar = ttk.Button(
            buttons_frame,
            text="🧹 Limpiar Filtros",
            command=self.limpiar_filtros,
            style="Secondary.TButton"
        )
        btn_limpiar.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Frame contenedor para tabla y detalles (layout vertical)
        table_details_container = tk.Frame(main_frame, bg=c["bg_darkest"])
        table_details_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        table_details_container.grid_rowconfigure(0, weight=2)  # Tabla ocupa más espacio vertical
        table_details_container.grid_rowconfigure(1, weight=1)  # Detalles ocupan menos espacio
        table_details_container.grid_columnconfigure(0, weight=1)
        
        # Frame de tabla (parte superior)
        table_frame = tk.Frame(table_details_container, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
        table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        table_title = tk.Label(
            table_frame,
            text="Ventas Registradas",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            pady=10
        )
        table_title.pack()
        
        # Frame para tabla con scrollbars usando grid para mejor control
        table_container = tk.Frame(table_frame, bg=c["bg_dark"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Scrollbar vertical estilizada
        v_scrollbar_table = ttk.Scrollbar(
            table_container,
            orient=tk.VERTICAL,
            style="Custom.Vertical.TScrollbar"
        )
        v_scrollbar_table.grid(row=0, column=1, sticky="ns")
        
        # Scrollbar horizontal estilizada
        h_scrollbar_table = ttk.Scrollbar(
            table_container,
            orient=tk.HORIZONTAL,
            style="Custom.Horizontal.TScrollbar"
        )
        h_scrollbar_table.grid(row=1, column=0, sticky="ew")
        
        # Treeview (tabla)
        columns = ("numero_factura", "fecha", "hora", "cliente_id", "subtotal", 
                  "descuento", "impuesto", "total", "metodo_pago")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=v_scrollbar_table.set,
            xscrollcommand=h_scrollbar_table.set
        )
        
        v_scrollbar_table.config(command=self.tree.yview)
        h_scrollbar_table.config(command=self.tree.xview)
        
        # Colocar la tabla en el grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Configurar columnas
        self.tree.heading("numero_factura", text="N° Factura")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("cliente_id", text="Cliente ID")
        self.tree.heading("subtotal", text="Subtotal")
        self.tree.heading("descuento", text="Descuento")
        self.tree.heading("impuesto", text="Impuesto")
        self.tree.heading("total", text="Total")
        self.tree.heading("metodo_pago", text="Método Pago")
        
        # Anchos de columnas
        self.tree.column("numero_factura", width=120, anchor=tk.CENTER)
        self.tree.column("fecha", width=100, anchor=tk.CENTER)
        self.tree.column("hora", width=80, anchor=tk.CENTER)
        self.tree.column("cliente_id", width=80, anchor=tk.CENTER)
        self.tree.column("subtotal", width=100, anchor=tk.E)
        self.tree.column("descuento", width=100, anchor=tk.E)
        self.tree.column("impuesto", width=100, anchor=tk.E)
        self.tree.column("total", width=120, anchor=tk.E)
        self.tree.column("metodo_pago", width=120, anchor=tk.CENTER)
        
        # Evento de selección para mostrar detalles
        self.tree.bind("<<TreeviewSelect>>", self.on_venta_selected)
        
        # Frame para detalles (parte inferior)
        self.detalle_container = tk.Frame(
            table_details_container,
            bg=c["bg_dark"],
            relief=tk.RAISED,
            bd=2
        )
        self.detalle_container.grid(row=1, column=0, sticky="nsew")
        
        # Título del panel de detalles
        detalle_title = tk.Label(
            self.detalle_container,
            text="📋 Detalles de la Venta",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            pady=10
        )
        detalle_title.pack()
        
        # Frame contenedor para canvas y scrollbars usando grid
        detalle_scroll_frame = tk.Frame(self.detalle_container, bg=c["bg_dark"])
        detalle_scroll_frame.pack(fill=tk.BOTH, expand=True)
        detalle_scroll_frame.grid_rowconfigure(0, weight=1)
        detalle_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Frame scrollable para el contenido de detalles
        detalle_canvas = tk.Canvas(
            detalle_scroll_frame,
            bg=c["bg_dark"],
            highlightthickness=0
        )
        detalle_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar vertical para el contenido de detalles
        detalle_v_scrollbar = ttk.Scrollbar(
            detalle_scroll_frame,
            orient=tk.VERTICAL,
            command=detalle_canvas.yview,
            style="Custom.Vertical.TScrollbar"
        )
        detalle_v_scrollbar.grid(row=0, column=1, sticky="ns")
        detalle_canvas.configure(yscrollcommand=detalle_v_scrollbar.set)
        
        # Scrollbar horizontal para el contenido de detalles
        detalle_h_scrollbar = ttk.Scrollbar(
            detalle_scroll_frame,
            orient=tk.HORIZONTAL,
            command=detalle_canvas.xview,
            style="Custom.Horizontal.TScrollbar"
        )
        detalle_h_scrollbar.grid(row=1, column=0, sticky="ew")
        detalle_canvas.configure(xscrollcommand=detalle_h_scrollbar.set)
        
        # Frame para el contenido de detalles (dentro del canvas)
        self.detalle_content = tk.Frame(detalle_canvas, bg=c["bg_dark"])
        detalle_canvas_window = detalle_canvas.create_window(
            (0, 0),
            window=self.detalle_content,
            anchor="nw"
        )
        
        # Configurar scroll del canvas
        def on_detalle_configure(event):
            # Actualizar scrollregion para ambos ejes
            bbox = detalle_canvas.bbox("all")
            if bbox:
                detalle_canvas.configure(scrollregion=bbox)
        
        def on_detalle_canvas_configure(event):
            # Ajustar ancho del contenido al ancho del canvas
            canvas_width = event.width
            detalle_canvas.itemconfig(detalle_canvas_window, width=canvas_width)
            # Actualizar scrollregion
            bbox = detalle_canvas.bbox("all")
            if bbox:
                detalle_canvas.configure(scrollregion=bbox)
        
        self.detalle_content.bind("<Configure>", on_detalle_configure)
        detalle_canvas.bind("<Configure>", on_detalle_canvas_configure)
        
        # Habilitar scroll con rueda del mouse
        def on_detalle_mousewheel(event):
            try:
                if detalle_canvas.winfo_exists():
                    detalle_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        def on_detalle_button4(event):
            try:
                if detalle_canvas.winfo_exists():
                    detalle_canvas.yview_scroll(-1, "units")
            except tk.TclError:
                pass
        
        def on_detalle_button5(event):
            try:
                if detalle_canvas.winfo_exists():
                    detalle_canvas.yview_scroll(1, "units")
            except tk.TclError:
                pass
        
        detalle_canvas.bind_all("<MouseWheel>", on_detalle_mousewheel, add="+")
        detalle_canvas.bind_all("<Button-4>", on_detalle_button4, add="+")
        detalle_canvas.bind_all("<Button-5>", on_detalle_button5, add="+")
        
        # Guardar referencia al canvas
        self.detalle_canvas = detalle_canvas
        
        # Mensaje inicial
        self.detalle_message = tk.Label(
            self.detalle_content,
            text="Seleccione una venta para ver sus detalles",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_muted"],
            bg=c["bg_dark"],
            wraplength=300
        )
        self.detalle_message.pack(expand=True, padx=10, pady=10)
        
        # Frame de totales
        total_frame = tk.Frame(main_frame, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
        total_frame.pack(fill=tk.X, pady=0)
        
        total_content = tk.Frame(total_frame, bg=c["bg_dark"])
        total_content.pack(fill=tk.X, padx=15, pady=15)
        
        self.total_label = tk.Label(
            total_content,
            text="TOTAL: $0.00",
            font=(Settings.FONT_PRIMARY, 16, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            anchor=tk.E
        )
        self.total_label.pack(fill=tk.X)
        
        self.cantidad_ventas_label = tk.Label(
            total_content,
            text="Cantidad de ventas: 0",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"],
            anchor=tk.E
        )
        self.cantidad_ventas_label.pack(fill=tk.X, pady=(5, 0))
    
    def parsear_fecha(self, fecha_str: str) -> Optional[date]:
        """Parsea una fecha en formato YYYY-MM-DD."""
        try:
            return datetime.strptime(fecha_str.strip(), "%Y-%m-%d").date()
        except:
            return None
    
    def parsear_hora(self, hora_str: str) -> Optional[time]:
        """Parsea una hora en formato HH:MM."""
        try:
            return datetime.strptime(hora_str.strip(), "%H:%M").time()
        except:
            return None
    
    def aplicar_filtros(self):
        """Aplica los filtros y actualiza la tabla."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener valores de filtros
        fecha_dia = None
        if self.fecha_dia_var.get().strip():
            fecha_dia = self.parsear_fecha(self.fecha_dia_var.get())
            if not fecha_dia:
                messagebox.showerror(
                    "Error",
                    "Formato de fecha inválido. Use YYYY-MM-DD",
                    parent=self.window
                )
                return
        
        mes = None
        if self.mes_var.get().strip():
            try:
                mes = int(self.mes_var.get())
                if mes < 1 or mes > 12:
                    raise ValueError
            except:
                messagebox.showerror(
                    "Error",
                    "El mes debe ser un número entre 1 y 12",
                    parent=self.window
                )
                return
        
        año = None
        if self.año_var.get().strip():
            try:
                año = int(self.año_var.get())
            except:
                messagebox.showerror(
                    "Error",
                    "El año debe ser un número válido",
                    parent=self.window
                )
                return
        
        hora_inicio = None
        if self.hora_inicio_var.get().strip():
            hora_inicio = self.parsear_hora(self.hora_inicio_var.get())
            if not hora_inicio:
                messagebox.showerror(
                    "Error",
                    "Formato de hora inválido. Use HH:MM",
                    parent=self.window
                )
                return
        
        hora_fin = None
        if self.hora_fin_var.get().strip():
            hora_fin = self.parsear_hora(self.hora_fin_var.get())
            if not hora_fin:
                messagebox.showerror(
                    "Error",
                    "Formato de hora inválido. Use HH:MM",
                    parent=self.window
                )
                return
        
        # Validar que si hay rango de horas, haya día específico
        if (hora_inicio or hora_fin) and not fecha_dia:
            messagebox.showerror(
                "Error",
                "El filtro de rango de horas requiere un día específico",
                parent=self.window
            )
            return
        
        # Obtener ventas filtradas
        try:
            ventas = self.service.obtener_ventas_filtradas(
                fecha_inicio=fecha_dia,
                fecha_fin=None,
                mes=mes,
                año=año,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            )
            
            # Limpiar mapeo de ventas
            self.ventas_dict = {}
            
            # Agregar ventas a la tabla
            for venta in ventas:
                fecha_str = venta.fecha.strftime("%Y-%m-%d") if venta.fecha else ""
                hora_str = venta.fecha.strftime("%H:%M") if venta.fecha else ""
                
                item_id = self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        venta.numero_factura,
                        fecha_str,
                        hora_str,
                        venta.cliente_id if venta.cliente_id else "",
                        f"${venta.subtotal:.2f}",
                        f"${venta.descuento_total:.2f}",
                        f"${venta.impuesto_total:.2f}",
                        f"${venta.total:.2f}",
                        venta.metodo_pago.value if hasattr(venta.metodo_pago, 'value') else str(venta.metodo_pago)
                    )
                )
                
                # Guardar mapeo de item del tree a ID de venta
                self.ventas_dict[item_id] = venta.id
            
            # Calcular y mostrar totales
            total = self.service.calcular_total_ventas(ventas)
            self.total_label.config(text=f"TOTAL: ${total:,.2f}")
            self.cantidad_ventas_label.config(text=f"Cantidad de ventas: {len(ventas)}")
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al cargar ventas: {str(e)}",
                parent=self.window
            )
    
    def limpiar_filtros(self):
        """Limpia todos los filtros y recarga todas las ventas."""
        self.fecha_dia_var.set("")
        self.mes_var.set("")
        self.año_var.set("")
        self.hora_inicio_var.set("")
        self.hora_fin_var.set("")
        # Cerrar detalles si están abiertos
        self.cerrar_detalles()
        self.aplicar_filtros()
    
    def on_venta_selected(self, event):
        """Maneja la selección de una venta en la tabla."""
        selection = self.tree.selection()
        if not selection:
            # Si no hay selección, mostrar mensaje inicial
            self.cerrar_detalles()
            return
        
        item_id = selection[0]
        venta_id = self.ventas_dict.get(item_id)
        
        if not venta_id:
            # Mostrar mensaje de error en el panel de detalles
            self.cerrar_detalles()
            error_label = tk.Label(
                self.detalle_content,
                text=f"Error: No se encontró el ID de la venta.\nItem ID: {item_id}",
                font=(Settings.FONT_PRIMARY, 10),
                fg=COLORS["red_primary"],
                bg=COLORS["bg_dark"],
                wraplength=300
            )
            error_label.pack(expand=True, padx=10, pady=10)
            self.detalle_canvas.update_idletasks()
            self.detalle_canvas.configure(scrollregion=self.detalle_canvas.bbox("all"))
            return
        
        # Si la misma venta ya está mostrada, no hacer nada
        if self.venta_expandida_id == venta_id:
            return
        
        # Mostrar detalles de la venta seleccionada
        try:
            self.mostrar_detalles_venta(item_id, venta_id)
        except Exception as e:
            import traceback
            error_msg = f"Error al mostrar detalles:\n{str(e)}"
            # Mostrar error en el panel de detalles en lugar de messagebox
            self.cerrar_detalles()
            error_label = tk.Label(
                self.detalle_content,
                text=error_msg,
                font=(Settings.FONT_PRIMARY, 10),
                fg=COLORS["red_primary"],
                bg=COLORS["bg_dark"],
                wraplength=300,
                justify=tk.LEFT
            )
            error_label.pack(expand=True, padx=10, pady=10)
            self.detalle_canvas.update_idletasks()
            self.detalle_canvas.configure(scrollregion=self.detalle_canvas.bbox("all"))
    
    def mostrar_detalles_venta(self, item_id: str, venta_id: int):
        """Muestra los detalles de una venta en el panel inferior."""
        c = COLORS
        
        # Limpiar contenido de detalles primero
        for widget in self.detalle_content.winfo_children():
            widget.destroy()
        
        # Ocultar mensaje inicial si está visible
        try:
            self.detalle_message.pack_forget()
        except:
            pass
        
        # Asegurar que el frame de detalles esté visible
        self.detalle_container.grid(row=1, column=0, sticky="nsew")
        
        # Obtener items de la venta (lazy load)
        try:
            items = self.service.obtener_items_venta(venta_id)
            if not items or len(items) == 0:
                # Si no hay items, mostrar mensaje
                no_items_label = tk.Label(
                    self.detalle_content,
                    text=f"No se encontraron productos para esta venta.\nVenta ID: {venta_id}",
                    font=(Settings.FONT_PRIMARY, 10),
                    fg=c["text_muted"],
                    bg=c["bg_dark"],
                    wraplength=300
                )
                no_items_label.pack(expand=True, padx=10, pady=10)
                self.detalle_canvas.update_idletasks()
                self.detalle_canvas.configure(scrollregion=self.detalle_canvas.bbox("all"))
                self.venta_expandida_id = venta_id
                return
        except Exception as e:
            import traceback
            error_msg = f"Error al cargar detalles:\nVenta ID: {venta_id}\nError: {str(e)}"
            print(f"DEBUG: Error al obtener items: {traceback.format_exc()}")
            error_label = tk.Label(
                self.detalle_content,
                text=error_msg,
                font=(Settings.FONT_PRIMARY, 9),
                fg=c["red_primary"],
                bg=c["bg_dark"],
                wraplength=300,
                justify=tk.LEFT
            )
            error_label.pack(expand=True, padx=10, pady=10)
            self.detalle_canvas.update_idletasks()
            self.detalle_canvas.configure(scrollregion=self.detalle_canvas.bbox("all"))
            return
        
        # Frame para información de la venta
        info_frame = tk.Frame(self.detalle_content, bg=c["bg_dark"])
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        # Obtener información de la venta seleccionada
        selected_item = self.tree.item(item_id)
        numero_factura = selected_item['values'][0]
        fecha = selected_item['values'][1]
        hora = selected_item['values'][2]
        total = selected_item['values'][7]
        
        # Mostrar información básica
        info_label = tk.Label(
            info_frame,
            text=f"Factura: {numero_factura}\nFecha: {fecha} {hora}\nTotal: {total}",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"],
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Frame para tabla de productos con scrollbars
        products_container = tk.Frame(self.detalle_content, bg=c["bg_dark"])
        products_container.pack(fill=tk.BOTH, expand=True)
        products_container.grid_rowconfigure(0, weight=1)
        products_container.grid_columnconfigure(0, weight=1)
        
        # Scrollbar vertical para productos
        v_scrollbar_products = ttk.Scrollbar(
            products_container,
            orient=tk.VERTICAL,
            style="Custom.Vertical.TScrollbar"
        )
        v_scrollbar_products.grid(row=0, column=1, sticky="ns")
        
        # Scrollbar horizontal para productos
        h_scrollbar_products = ttk.Scrollbar(
            products_container,
            orient=tk.HORIZONTAL,
            style="Custom.Horizontal.TScrollbar"
        )
        h_scrollbar_products.grid(row=1, column=0, sticky="ew")
        
        # Crear tabla de productos
        products_columns = ("nombre", "cantidad", "precio_unit", "ganancia_unit", "subtotal")
        products_tree = ttk.Treeview(
            products_container,
            columns=products_columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=v_scrollbar_products.set,
            xscrollcommand=h_scrollbar_products.set
        )
        
        v_scrollbar_products.config(command=products_tree.yview)
        h_scrollbar_products.config(command=products_tree.xview)
        
        # Configurar columnas
        products_tree.heading("nombre", text="Producto")
        products_tree.heading("cantidad", text="Cant.")
        products_tree.heading("precio_unit", text="Precio Unit.")
        products_tree.heading("ganancia_unit", text="Ganancia")
        products_tree.heading("subtotal", text="Subtotal")
        
        products_tree.column("nombre", width=150, anchor=tk.W)
        products_tree.column("cantidad", width=60, anchor=tk.CENTER)
        products_tree.column("precio_unit", width=90, anchor=tk.E)
        products_tree.column("ganancia_unit", width=80, anchor=tk.E)
        products_tree.column("subtotal", width=90, anchor=tk.E)
        
        # Variables para calcular ganancia total
        ganancia_total_venta = 0.0
        
        # Agregar productos a la tabla
        for item in items:
            # Calcular ganancia unitaria y total por item
            ganancia_unit = 0.0
            ganancia_item_total = 0.0
            precio_base = 0.0
            
            try:
                from ...repository.product_repository import ProductRepository
                product_repo = ProductRepository()
                producto = product_repo.get_by_code(item.codigo_producto)
                if producto:
                    ganancia_unit = producto.calcular_ganancia_unitaria()
                    precio_base = producto.precio_unitario
                    # Ganancia total del item = ganancia unitaria * cantidad
                    ganancia_item_total = ganancia_unit * item.cantidad
                    ganancia_total_venta += ganancia_item_total
            except:
                # Si no se puede obtener el producto, calcular ganancia aproximada
                # precio_unitario en ItemVenta es valor_venta, así que necesitamos el precio_base
                # Por ahora, si no hay producto, la ganancia será 0
                pass
            
            subtotal_item = item.calcular_total()
            
            products_tree.insert(
                "",
                tk.END,
                values=(
                    item.nombre_producto,
                    item.cantidad,
                    f"${item.precio_unitario:.2f}",
                    f"${ganancia_unit:.2f}",
                    f"${subtotal_item:.2f}"
                )
            )
        
        products_tree.grid(row=0, column=0, sticky="nsew")
        
        # Frame para resumen de ganancias (debajo de la tabla de productos)
        ganancia_summary_frame = tk.Frame(self.detalle_content, bg=c["bg_dark"], relief=tk.RAISED, bd=1)
        ganancia_summary_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        # Título del resumen de ganancias
        ganancia_title = tk.Label(
            ganancia_summary_frame,
            text="💰 Resumen de Ganancias",
            font=(Settings.FONT_PRIMARY, 11, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            pady=5
        )
        ganancia_title.pack()
        
        # Información de ganancias
        ganancia_info_frame = tk.Frame(ganancia_summary_frame, bg=c["bg_dark"])
        ganancia_info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Calcular otros totales
        subtotal_venta = sum(item.calcular_subtotal() for item in items)
        total_venta = sum(item.calcular_total() for item in items)
        
        # Mostrar ganancia total destacada
        ganancia_total_label = tk.Label(
            ganancia_info_frame,
            text=f"Ganancia Total de la Venta: ${ganancia_total_venta:,.2f}",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"]
        )
        ganancia_total_label.pack(anchor=tk.W, pady=5)
        
        # Mostrar información adicional
        info_extra = tk.Label(
            ganancia_info_frame,
            text=f"Subtotal productos: ${subtotal_venta:,.2f}\n"
                 f"Total venta: ${total_venta:,.2f}\n"
                 f"Ganancia obtenida: ${ganancia_total_venta:,.2f}",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"],
            justify=tk.LEFT
        )
        info_extra.pack(anchor=tk.W, pady=(5, 0))
        
        # Forzar actualización del canvas
        self.detalle_content.update_idletasks()
        self.detalle_canvas.update_idletasks()
        
        # Configurar scrollregion después de que todos los widgets estén creados
        def update_scrollregion():
            try:
                bbox = self.detalle_canvas.bbox("all")
                if bbox:
                    self.detalle_canvas.configure(scrollregion=bbox)
            except:
                pass
        
        # Actualizar después de un pequeño delay para asegurar que todo esté renderizado
        self.window.after(100, update_scrollregion)
        
        # Guardar referencia
        self.venta_expandida_id = venta_id
    
    def cerrar_detalles(self):
        """Limpia el panel de detalles y muestra el mensaje inicial."""
        # Limpiar contenido de detalles
        for widget in self.detalle_content.winfo_children():
            widget.destroy()
        
        # Mostrar mensaje inicial
        self.detalle_message.pack(expand=True)
        
        # Limpiar referencia
        self.venta_expandida_id = None


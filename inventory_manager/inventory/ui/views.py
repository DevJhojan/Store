"""Vista de la interfaz gráfica del módulo de Inventarios."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional

from ...config.settings import Settings, COLORS
from ...services.inventory_service import InventoryService
from ...utils.validators import validate_fields, parse_numeric_field
from ...ui.styles import StyleManager


class InventoryGUI:
    """Interfaz gráfica del módulo de gestión de inventarios."""
    
    def __init__(self, parent_window, service: Optional[InventoryService] = None):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            parent_window: Ventana padre (Tk o Toplevel)
            service: Servicio de inventario (si None, se crea uno nuevo)
        """
        self.parent = parent_window
        self.service = service or InventoryService()
        
        # Crear ventana Toplevel si el padre es Tk
        if isinstance(parent_window, tk.Tk):
            self.window = tk.Toplevel(parent_window)
        else:
            self.window = parent_window
        
        # Configurar ventana
        self.window.title("⚡ Gestión de Inventarios")
        self.window.configure(bg=COLORS["bg_darkest"])
        self.window.resizable(True, True)
        
        # Maximizar la ventana (compatible con todos los sistemas)
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
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Diccionario de campos de entrada
        self.entries: Dict[str, tk.Entry] = {}
        self.ganancia_entry: Optional[tk.Entry] = None
        
        # Producto seleccionado para actualizar
        self.producto_seleccionado: Optional[str] = None
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar productos
        self.refresh()
    
    def generar_codigo_autoincremental(self) -> str:
        """
        Genera un código autoincremental para un nuevo producto.
        
        Returns:
            str: Código generado (PROD001, PROD002, etc.)
        """
        productos = self.service.obtener_todos_los_productos()
        
        if not productos:
            return "PROD001"
        
        # Buscar el mayor número de código existente
        max_num = 0
        for producto in productos:
            if producto.codigo.startswith("PROD"):
                try:
                    num = int(producto.codigo[4:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        
        # Generar nuevo código
        nuevo_num = max_num + 1
        return f"PROD{nuevo_num:03d}"
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        c = COLORS
        
        # Frame principal con grid
        main_frame = tk.Frame(self.window, bg=c["bg_darkest"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar grid
        main_frame.grid_columnconfigure(0, weight=0, minsize=200)  # Panel lateral
        main_frame.grid_columnconfigure(1, weight=1)  # Contenido principal
        main_frame.grid_rowconfigure(0, weight=0)  # Formulario
        main_frame.grid_rowconfigure(1, weight=0)  # Botones
        main_frame.grid_rowconfigure(2, weight=1)  # Tabla y resumen
        
        # ========== PANEL LATERAL IZQUIERDO (Código) ==========
        lateral_frame = tk.Frame(main_frame, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
        lateral_frame.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(0, 10), pady=0)
        lateral_frame.grid_propagate(False)
        lateral_frame.config(width=200)
        
        # Título del panel lateral
        lateral_title = tk.Label(
            lateral_frame,
            text="Código",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            pady=15
        )
        lateral_title.pack()
        
        # Información sobre código autoincremental
        info_label = tk.Label(
            lateral_frame,
            text="Código auto\nincrementable,\nno editable",
            font=(Settings.FONT_PRIMARY, 9),
            fg=c["text_secondary"],
            bg=c["bg_dark"],
            justify=tk.CENTER,
            wraplength=180,
            pady=10
        )
        info_label.pack()
        
        # Campo código (solo lectura)
        self.entries["codigo_lateral"] = tk.Entry(
            lateral_frame,
            font=(Settings.FONT_PRIMARY, 14, "bold"),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT,
            state="readonly",
            justify=tk.CENTER,
            readonlybackground=c["bg_medium"]
        )
        self.entries["codigo_lateral"].pack(fill=tk.X, padx=15, pady=10)
        
        # ========== FORMULARIO PRINCIPAL (Parte Superior) ==========
        form_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        form_frame.grid(row=0, column=1, sticky="ew", padx=0, pady=(0, 15))
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)
        
        # Fila 1: Código, Nombre, Categoría
        # Código (sincronizado con panel lateral)
        codigo_label = tk.Label(
            form_frame,
            text="Código",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_darkest"]
        )
        codigo_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        
        self.entries["codigo"] = tk.Entry(
            form_frame,
            font=(Settings.FONT_PRIMARY, 11),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT,
            state="readonly",
            readonlybackground=c["bg_medium"]
        )
        self.entries["codigo"].grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 15))
        
        # Nombre
        nombre_label = tk.Label(
            form_frame,
            text="Nombre",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_darkest"]
        )
        nombre_label.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(0, 5))
        
        self.entries["nombre"] = tk.Entry(
            form_frame,
            font=(Settings.FONT_PRIMARY, 11),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT,
            insertbackground=c["text_primary"]
        )
        self.entries["nombre"].grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))
        
        # Categoría
        categoria_label = tk.Label(
            form_frame,
            text="Categoría",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_darkest"]
        )
        categoria_label.grid(row=0, column=2, sticky="w", padx=0, pady=(0, 5))
        
        self.entries["categoria"] = tk.Entry(
            form_frame,
            font=(Settings.FONT_PRIMARY, 11),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT,
            insertbackground=c["text_primary"]
        )
        self.entries["categoria"].grid(row=1, column=2, sticky="ew", padx=0, pady=(0, 15))
        
        # Fila 2: Cantidad, Precio unitario, Ganancia
        # Cantidad
        cantidad_label = tk.Label(
            form_frame,
            text="Cantidad",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_darkest"]
        )
        cantidad_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 5))
        
        self.entries["cantidad"] = tk.Entry(
            form_frame,
            font=(Settings.FONT_PRIMARY, 11),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT,
            insertbackground=c["text_primary"]
        )
        self.entries["cantidad"].grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 0))
        
        # Precio unitario
        precio_label = tk.Label(
            form_frame,
            text="Precio unitario",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_darkest"]
        )
        precio_label.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=(0, 5))
        
        self.entries["precio_unitario"] = tk.Entry(
            form_frame,
            font=(Settings.FONT_PRIMARY, 11),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT,
            insertbackground=c["text_primary"]
        )
        self.entries["precio_unitario"].grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=(0, 0))
        
        # Ganancia (%)
        ganancia_label = tk.Label(
            form_frame,
            text="Ganancia (%)",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_darkest"]
        )
        ganancia_label.grid(row=2, column=2, sticky="w", padx=0, pady=(0, 5))
        
        self.ganancia_entry = tk.Entry(
            form_frame,
            font=(Settings.FONT_PRIMARY, 11),
            bg=c["bg_medium"],
            fg=c["text_primary"],
            relief=tk.FLAT,
            insertbackground=c["text_primary"]
        )
        self.ganancia_entry.grid(row=3, column=2, sticky="ew", padx=0, pady=(0, 0))
        self.ganancia_entry.insert(0, "0")
        
        # ========== BARRA DE BOTONES ==========
        buttons_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        buttons_frame.grid(row=1, column=1, sticky="ew", padx=0, pady=(0, 15))
        
        btn_agregar = ttk.Button(
            buttons_frame,
            text="Agregar",
            command=self.agregar_producto,
            style="Accent.TButton"
        )
        btn_agregar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_actualizar = ttk.Button(
            buttons_frame,
            text="Actualizar",
            command=self.actualizar_producto,
            style="Accent.TButton"
        )
        btn_actualizar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_eliminar = ttk.Button(
            buttons_frame,
            text="Eliminar",
            command=self.eliminar_producto,
            style="Accent.TButton"
        )
        btn_eliminar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_limpiar = ttk.Button(
            buttons_frame,
            text="Limpiar",
            command=self.limpiar_formulario,
            style="Secondary.TButton"
        )
        btn_limpiar.pack(side=tk.LEFT)
        
        # ========== SECCIÓN INFERIOR (Tabla y Resumen) ==========
        bottom_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        bottom_frame.grid(row=2, column=1, sticky="nsew", padx=0, pady=0)
        bottom_frame.grid_columnconfigure(0, weight=3)  # Tabla (más espacio)
        bottom_frame.grid_columnconfigure(1, weight=1)  # Resumen (menos espacio)
        
        # Panel izquierdo: Tabla de datos
        table_frame = tk.Frame(bottom_frame, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        table_title = tk.Label(
            table_frame,
            text="Tabla de datos",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            pady=10
        )
        table_title.pack()
        
        # Frame para tabla con scrollbars
        table_container = tk.Frame(table_frame, bg=c["bg_dark"])
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview (tabla)
        columns = ("codigo", "nombre", "categoria", "cantidad", "precio_unitario", 
                  "valor_base", "valor_ganancia", "subtotal")
        
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Configurar columnas
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("cantidad", text="Cantidad")
        self.tree.heading("precio_unitario", text="Precio Unit.")
        self.tree.heading("valor_base", text="Valor Base")
        self.tree.heading("valor_ganancia", text="Valor Ganancia")
        self.tree.heading("subtotal", text="Subtotal")
        
        # Anchos de columnas
        self.tree.column("codigo", width=100, anchor=tk.CENTER)
        self.tree.column("nombre", width=150, anchor=tk.W)
        self.tree.column("categoria", width=120, anchor=tk.W)
        self.tree.column("cantidad", width=80, anchor=tk.CENTER)
        self.tree.column("precio_unitario", width=100, anchor=tk.E)
        self.tree.column("valor_base", width=100, anchor=tk.E)
        self.tree.column("valor_ganancia", width=120, anchor=tk.E)
        self.tree.column("subtotal", width=100, anchor=tk.E)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.on_producto_seleccionado)
        
        # Panel derecho: Resumen total
        summary_frame = tk.Frame(bottom_frame, bg=c["bg_dark"], relief=tk.RAISED, bd=2)
        summary_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        summary_title = tk.Label(
            summary_frame,
            text="Resumen Total",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            pady=15
        )
        summary_title.pack()
        
        # Contenedor de resumen
        summary_content = tk.Frame(summary_frame, bg=c["bg_dark"])
        summary_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Labels de resumen
        self.total_productos_label = tk.Label(
            summary_content,
            text="Total Productos: 0",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"],
            anchor=tk.W
        )
        self.total_productos_label.pack(fill=tk.X, pady=(0, 10))
        
        self.valor_total_base_label = tk.Label(
            summary_content,
            text="Valor Total Base: $0.00",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"],
            anchor=tk.W
        )
        self.valor_total_base_label.pack(fill=tk.X, pady=(0, 10))
        
        self.valor_total_ganancia_label = tk.Label(
            summary_content,
            text="Valor Total Ganancia: $0.00",
            font=(Settings.FONT_PRIMARY, 10),
            fg=c["text_secondary"],
            bg=c["bg_dark"],
            anchor=tk.W
        )
        self.valor_total_ganancia_label.pack(fill=tk.X, pady=(0, 10))
        
        # Separador
        separator = tk.Frame(summary_content, bg=c["red_primary"], height=2)
        separator.pack(fill=tk.X, pady=15)
        
        self.valor_total_subtotal_label = tk.Label(
            summary_content,
            text="TOTAL: $0.00",
            font=(Settings.FONT_PRIMARY, 12, "bold"),
            fg=c["red_primary"],
            bg=c["bg_dark"],
            anchor=tk.W
        )
        self.valor_total_subtotal_label.pack(fill=tk.X, pady=(10, 0))
        
        # Generar código inicial
        self.limpiar_formulario()
    
    def calcular_valores_producto(self, cantidad: int, precio_unitario: float, ganancia: float) -> tuple:
        """
        Calcula los valores financieros de un producto.
        
        Args:
            cantidad: Cantidad del producto
            precio_unitario: Precio unitario
            ganancia: Porcentaje de ganancia
            
        Returns:
            tuple: (valor_base, valor_ganancia, subtotal)
        """
        valor_base = cantidad * precio_unitario
        valor_ganancia = valor_base * (ganancia / 100.0)
        subtotal = valor_base + valor_ganancia
        return valor_base, valor_ganancia, subtotal
    
    def on_producto_seleccionado(self, event):
        """Maneja la selección de un producto en la tabla."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        valores = item['values']
        
        if len(valores) >= 5:
            codigo = valores[0]
            self.producto_seleccionado = codigo
            
            # Cargar datos del producto
            producto = self.service.obtener_producto_por_codigo(codigo)
            if producto:
                self.entries["codigo"].config(state="normal")
                self.entries["codigo"].delete(0, tk.END)
                self.entries["codigo"].insert(0, producto.codigo)
                self.entries["codigo"].config(state="readonly")
                
                self.entries["codigo_lateral"].config(state="normal")
                self.entries["codigo_lateral"].delete(0, tk.END)
                self.entries["codigo_lateral"].insert(0, producto.codigo)
                self.entries["codigo_lateral"].config(state="readonly")
                
                self.entries["nombre"].delete(0, tk.END)
                self.entries["nombre"].insert(0, producto.nombre)
                
                self.entries["categoria"].delete(0, tk.END)
                self.entries["categoria"].insert(0, producto.categoria)
                
                self.entries["cantidad"].delete(0, tk.END)
                self.entries["cantidad"].insert(0, str(producto.cantidad))
                
                self.entries["precio_unitario"].delete(0, tk.END)
                self.entries["precio_unitario"].insert(0, str(producto.precio_unitario))
                
                # Calcular ganancia desde los valores de la tabla si están disponibles
                if len(valores) >= 8:
                    try:
                        valor_base = float(valores[5])
                        valor_ganancia = float(valores[6])
                        if valor_base > 0:
                            ganancia_calculada = (valor_ganancia / valor_base) * 100
                            self.ganancia_entry.delete(0, tk.END)
                            self.ganancia_entry.insert(0, f"{ganancia_calculada:.2f}")
                    except (ValueError, IndexError):
                        self.ganancia_entry.delete(0, tk.END)
                        self.ganancia_entry.insert(0, "0")
                else:
                    self.ganancia_entry.delete(0, tk.END)
                    self.ganancia_entry.insert(0, "0")
    
    def agregar_producto(self):
        """Agrega un nuevo producto al inventario."""
        # Validar campos requeridos
        campos_requeridos = {
            "nombre": "Nombre",
            "categoria": "Categoría",
            "cantidad": "Cantidad",
            "precio_unitario": "Precio unitario"
        }
        
        es_valido, key, nombre = validate_fields(
            {k: self.entries[k] for k in campos_requeridos.keys()},
            campos_requeridos
        )
        
        if not es_valido:
            messagebox.showerror("Error", f"El campo '{nombre}' es obligatorio.", parent=self.window)
            return
        
        # Parsear valores numéricos
        cantidad_ok, cantidad, error_cantidad = parse_numeric_field(
            self.entries["cantidad"].get(), int
        )
        if not cantidad_ok:
            messagebox.showerror("Error", f"Cantidad: {error_cantidad}", parent=self.window)
            return
        
        precio_ok, precio, error_precio = parse_numeric_field(
            self.entries["precio_unitario"].get(), float
        )
        if not precio_ok:
            messagebox.showerror("Error", f"Precio unitario: {error_precio}", parent=self.window)
            return
        
        # Parsear ganancia
        ganancia_ok, ganancia, error_ganancia = parse_numeric_field(
            self.ganancia_entry.get(), float
        )
        if not ganancia_ok:
            ganancia = 0.0
        
        # Obtener código (generar si no existe)
        codigo = self.entries["codigo"].get().strip()
        if not codigo:
            codigo = self.generar_codigo_autoincremental()
        
        # Agregar producto usando el servicio
        exito, mensaje = self.service.agregar_producto(
            codigo=codigo,
            nombre=self.entries["nombre"].get().strip(),
            categoria=self.entries["categoria"].get().strip(),
            cantidad=cantidad,
            precio_unitario=precio
        )
        
        if exito:
            messagebox.showinfo("Éxito", mensaje, parent=self.window)
            self.limpiar_formulario()
            self.refresh()
        else:
            messagebox.showerror("Error", mensaje, parent=self.window)
    
    def actualizar_producto(self):
        """Actualiza un producto existente."""
        if not self.producto_seleccionado:
            messagebox.showerror("Error", "Debe seleccionar un producto de la tabla para actualizar.", parent=self.window)
            return
        
        # Validar campos
        campos_requeridos = {
            "nombre": "Nombre",
            "categoria": "Categoría",
            "cantidad": "Cantidad",
            "precio_unitario": "Precio unitario"
        }
        
        es_valido, key, nombre = validate_fields(
            {k: self.entries[k] for k in campos_requeridos.keys()},
            campos_requeridos
        )
        
        if not es_valido:
            messagebox.showerror("Error", f"El campo '{nombre}' es obligatorio.", parent=self.window)
            return
        
        # Parsear valores
        cantidad_ok, cantidad, error_cantidad = parse_numeric_field(
            self.entries["cantidad"].get(), int
        )
        if not cantidad_ok:
            messagebox.showerror("Error", f"Cantidad: {error_cantidad}", parent=self.window)
            return
        
        precio_ok, precio, error_precio = parse_numeric_field(
            self.entries["precio_unitario"].get(), float
        )
        if not precio_ok:
            messagebox.showerror("Error", f"Precio unitario: {error_precio}", parent=self.window)
            return
        
        codigo_original = self.producto_seleccionado
        codigo_nuevo = self.entries["codigo"].get().strip()
        
        # Actualizar producto
        exito, mensaje = self.service.actualizar_producto(
            codigo_original=codigo_original,
            codigo=codigo_nuevo,
            nombre=self.entries["nombre"].get().strip(),
            categoria=self.entries["categoria"].get().strip(),
            cantidad=cantidad,
            precio_unitario=precio
        )
        
        if exito:
            messagebox.showinfo("Éxito", mensaje, parent=self.window)
            self.producto_seleccionado = None
            self.limpiar_formulario()
            self.refresh()
        else:
            messagebox.showerror("Error", mensaje, parent=self.window)
    
    def eliminar_producto(self):
        """Elimina un producto del inventario."""
        if not self.producto_seleccionado:
            messagebox.showerror("Error", "Debe seleccionar un producto de la tabla para eliminar.", parent=self.window)
            return
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el producto '{self.producto_seleccionado}'?",
            parent=self.window
        )
        
        if not respuesta:
            return
        
        # Eliminar producto
        exito, mensaje = self.service.eliminar_producto(self.producto_seleccionado)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje, parent=self.window)
            self.producto_seleccionado = None
            self.limpiar_formulario()
            self.refresh()
        else:
            messagebox.showerror("Error", mensaje, parent=self.window)
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        # Generar nuevo código
        nuevo_codigo = self.generar_codigo_autoincremental()
        
        # Limpiar campos
        self.entries["codigo"].config(state="normal")
        self.entries["codigo"].delete(0, tk.END)
        self.entries["codigo"].insert(0, nuevo_codigo)
        self.entries["codigo"].config(state="readonly")
        
        self.entries["codigo_lateral"].config(state="normal")
        self.entries["codigo_lateral"].delete(0, tk.END)
        self.entries["codigo_lateral"].insert(0, nuevo_codigo)
        self.entries["codigo_lateral"].config(state="readonly")
        
        self.entries["nombre"].delete(0, tk.END)
        self.entries["categoria"].delete(0, tk.END)
        self.entries["cantidad"].delete(0, tk.END)
        self.entries["precio_unitario"].delete(0, tk.END)
        
        if self.ganancia_entry:
            self.ganancia_entry.delete(0, tk.END)
            self.ganancia_entry.insert(0, "0")
        
        self.producto_seleccionado = None
        
        # Deseleccionar en tabla
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def refresh(self):
        """Actualiza la tabla y el resumen."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener todos los productos
        productos = self.service.obtener_todos_los_productos()
        
        # Variables para resumen
        total_productos = len(productos)
        valor_total_base = 0.0
        valor_total_ganancia = 0.0
        valor_total_subtotal = 0.0
        
        # Agregar productos a la tabla
        for producto in productos:
            # Obtener ganancia (por defecto 0 si no se puede calcular)
            ganancia = 0.0
            try:
                # Intentar obtener ganancia desde algún almacenamiento
                # Por ahora, usaremos 0 como predeterminado
                # En una implementación real, podrías almacenar la ganancia en la BD
                pass
            except:
                ganancia = 0.0
            
            # Calcular valores
            valor_base, valor_ganancia, subtotal = self.calcular_valores_producto(
                producto.cantidad,
                producto.precio_unitario,
                ganancia
            )
            
            # Agregar a tabla
            self.tree.insert(
                "",
                tk.END,
                values=(
                    producto.codigo,
                    producto.nombre,
                    producto.categoria,
                    producto.cantidad,
                    f"${producto.precio_unitario:.2f}",
                    f"${valor_base:.2f}",
                    f"${valor_ganancia:.2f}",
                    f"${subtotal:.2f}"
                )
            )
            
            # Acumular para resumen
            valor_total_base += valor_base
            valor_total_ganancia += valor_ganancia
            valor_total_subtotal += subtotal
        
        # Actualizar resumen
        self.total_productos_label.config(text=f"Total Productos: {total_productos}")
        self.valor_total_base_label.config(text=f"Valor Total Base: ${valor_total_base:,.2f}")
        self.valor_total_ganancia_label.config(text=f"Valor Total Ganancia: ${valor_total_ganancia:,.2f}")
        self.valor_total_subtotal_label.config(text=f"TOTAL: ${valor_total_subtotal:,.2f}")


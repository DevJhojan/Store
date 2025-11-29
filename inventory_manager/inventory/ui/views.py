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
        self.window.geometry(Settings.WINDOW_GEOMETRY)
        self.window.configure(bg=COLORS["bg_darkest"])
        self.window.resizable(True, True)
        
        # Manejar cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar productos existentes
        self.load_products()
        
        # Actualizar valor total
        self.update_total_value()
    
    def on_close(self):
        """Maneja el cierre de la ventana."""
        self.window.destroy()
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz."""
        c = COLORS
        
        # Frame principal con borde rojo
        main_frame = tk.Frame(self.window, bg=c["bg_darkest"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Título con estilo cyberpunk
        title_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Línea decorativa superior
        tk.Frame(title_frame, bg=c["red_primary"], height=2).pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="◆ SISTEMA DE GESTIÓN DE INVENTARIOS ◆",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_LARGE, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="[ Control Digital de Productos ]",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_muted"],
            bg=c["bg_darkest"]
        )
        subtitle_label.pack(pady=(2, 0))
        
        # Línea decorativa inferior
        tk.Frame(title_frame, bg=c["red_primary"], height=2).pack(fill=tk.X, pady=(10, 0))
        
        # Frame para formulario con borde rojo
        form_container = tk.Frame(main_frame, bg=c["red_dark"], padx=2, pady=2)
        form_container.pack(fill=tk.X, pady=(0, 15))
        
        form_frame = tk.Frame(form_container, bg=c["bg_dark"], padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear campos del formulario
        self.create_form_fields(form_frame)
        
        # Frame para botones
        button_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.create_buttons(button_frame)
        
        # Frame para la tabla con borde rojo
        table_container = tk.Frame(main_frame, bg=c["red_dark"], padx=2, pady=2)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        table_frame = tk.Frame(table_container, bg=c["bg_dark"])
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_table(table_frame)
        
        # Frame para el valor total con borde rojo brillante
        total_container = tk.Frame(main_frame, bg=c["red_primary"], padx=2, pady=2)
        total_container.pack(fill=tk.X, pady=(15, 0))
        
        total_frame = tk.Frame(total_container, bg=c["bg_dark"], padx=20, pady=12)
        total_frame.pack(fill=tk.BOTH, expand=True)
        
        self.total_label = tk.Label(
            total_frame,
            text="◈ VALOR TOTAL DEL INVENTARIO: $0.00",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_MEDIUM, "bold"),
            fg=c["success"],
            bg=c["bg_dark"]
        )
        self.total_label.pack()
    
    def create_form_fields(self, parent: tk.Frame):
        """Crear los campos del formulario."""
        c = COLORS
        
        # Configurar grid
        for i in range(5):
            parent.columnconfigure(i * 2, weight=0)
            parent.columnconfigure(i * 2 + 1, weight=1)
        
        self.entries: Dict[str, tk.Entry] = {}
        
        label_style = {
            "font": (Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL, "bold"),
            "fg": c["red_primary"],
            "bg": c["bg_dark"]
        }
        entry_style = {
            "font": (Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            "bg": c["bg_darkest"],
            "fg": c["text_primary"],
            "insertbackground": c["red_primary"],
            "relief": "flat",
            "highlightthickness": 2,
            "highlightbackground": c["red_dark"],
            "highlightcolor": c["red_bright"],
            "selectbackground": c["red_primary"],
            "selectforeground": c["text_primary"]
        }
        
        # Primera fila: Código, Nombre, Categoría
        row1_fields = [("codigo", "► CÓDIGO:"), ("nombre", "► NOMBRE:"), ("categoria", "► CATEGORÍA:")]
        for col, (key, label_text) in enumerate(row1_fields):
            tk.Label(parent, text=label_text, **label_style).grid(
                row=0, column=col * 2, sticky="e", padx=(15, 8), pady=8
            )
            entry = tk.Entry(parent, width=18, **entry_style)
            entry.grid(row=0, column=col * 2 + 1, sticky="ew", padx=(0, 15), pady=8, ipady=5)
            self.entries[key] = entry
        
        # Segunda fila: Cantidad, Precio Unitario
        row2_fields = [("cantidad", "► CANTIDAD:"), ("precio_unitario", "► PRECIO UNIT:")]
        for col, (key, label_text) in enumerate(row2_fields):
            tk.Label(parent, text=label_text, **label_style).grid(
                row=1, column=col * 2, sticky="e", padx=(15, 8), pady=8
            )
            entry = tk.Entry(parent, width=18, **entry_style)
            entry.grid(row=1, column=col * 2 + 1, sticky="ew", padx=(0, 15), pady=8, ipady=5)
            self.entries[key] = entry
    
    def create_buttons(self, parent: tk.Frame):
        """Crear los botones de acción."""
        buttons_info = [
            ("➕ Agregar", self.add_product, "Accent.TButton"),
            ("✏️ Actualizar", self.update_product, "Secondary.TButton"),
            ("🗑️ Eliminar", self.delete_product, "Secondary.TButton"),
            ("🔄 Limpiar", self.clear_form, "Secondary.TButton"),
            ("📊 Recalcular Total", self.update_total_value, "Secondary.TButton"),
        ]
        
        for text, command, style in buttons_info:
            btn = ttk.Button(parent, text=text, command=command, style=style)
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_table(self, parent: tk.Frame):
        """Crear la tabla de productos."""
        # Scrollbar con estilo personalizado
        scrollbar = ttk.Scrollbar(parent, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("codigo", "nombre", "categoria", "cantidad", "precio_unitario", "subtotal")
        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scrollbar.set
        )
        
        # Configurar columnas
        headings = {
            "codigo": "Código",
            "nombre": "Nombre",
            "categoria": "Categoría",
            "cantidad": "Cantidad",
            "precio_unitario": "Precio Unit.",
            "subtotal": "Subtotal"
        }
        
        widths = {
            "codigo": 100,
            "nombre": 200,
            "categoria": 120,
            "cantidad": 80,
            "precio_unitario": 100,
            "subtotal": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.tree.yview)
        
        # Evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def load_products(self):
        """Cargar productos desde el servicio."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener productos
        products = self.service.obtener_todos_los_productos()
        
        # Insertar en tabla
        for product in products:
            subtotal = product.calcular_subtotal()
            self.tree.insert("", tk.END, values=(
                product.codigo,
                product.nombre,
                product.categoria,
                product.cantidad,
                f"${product.precio_unitario:.2f}",
                f"${subtotal:.2f}"
            ))
    
    def refresh(self):
        """Actualizar la vista (usado después de cambios externos)."""
        self.load_products()
        self.update_total_value()
    
    def add_product(self):
        """Agregar un nuevo producto."""
        # Validar campos
        es_valido, key_campo_vacio, nombre_campo_vacio = validate_fields(self.entries, Settings.FIELD_NAMES)
        if not es_valido:
            messagebox.showerror("Error", f"El campo '{nombre_campo_vacio}' es obligatorio.")
            self.entries[key_campo_vacio].focus()
            return
        
        # Parsear y validar campos numéricos
        cantidad_exitoso, cantidad, msg_cantidad = parse_numeric_field(
            self.entries["cantidad"].get().strip(), int
        )
        if not cantidad_exitoso:
            messagebox.showerror("Error", f"Cantidad: {msg_cantidad}")
            self.entries["cantidad"].focus()
            return
        
        precio_exitoso, precio, msg_precio = parse_numeric_field(
            self.entries["precio_unitario"].get().strip(), float
        )
        if not precio_exitoso:
            messagebox.showerror("Error", f"Precio Unitario: {msg_precio}")
            self.entries["precio_unitario"].focus()
            return
        
        # Agregar producto usando el servicio
        codigo = self.entries["codigo"].get().strip()
        nombre = self.entries["nombre"].get().strip()
        categoria = self.entries["categoria"].get().strip()
        
        exitoso, mensaje = self.service.agregar_producto(
            codigo, nombre, categoria, cantidad, precio
        )
        
        if exitoso:
            messagebox.showinfo("Éxito", mensaje)
            self.clear_form()
            self.load_products()
            self.update_total_value()
        else:
            messagebox.showerror("Error", mensaje)
    
    def update_product(self):
        """Actualizar un producto existente."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para actualizar.")
            return
        
        # Validar campos
        es_valido, key_campo_vacio, nombre_campo_vacio = validate_fields(self.entries, Settings.FIELD_NAMES)
        if not es_valido:
            messagebox.showerror("Error", f"El campo '{nombre_campo_vacio}' es obligatorio.")
            self.entries[key_campo_vacio].focus()
            return
        
        # Parsear y validar campos numéricos
        cantidad_exitoso, cantidad, msg_cantidad = parse_numeric_field(
            self.entries["cantidad"].get().strip(), int
        )
        if not cantidad_exitoso:
            messagebox.showerror("Error", f"Cantidad: {msg_cantidad}")
            self.entries["cantidad"].focus()
            return
        
        precio_exitoso, precio, msg_precio = parse_numeric_field(
            self.entries["precio_unitario"].get().strip(), float
        )
        if not precio_exitoso:
            messagebox.showerror("Error", f"Precio Unitario: {msg_precio}")
            self.entries["precio_unitario"].focus()
            return
        
        # Obtener código original del producto seleccionado
        original_codigo = str(self.tree.item(selected[0])["values"][0])
        
        # Actualizar producto usando el servicio
        codigo = self.entries["codigo"].get().strip()
        nombre = self.entries["nombre"].get().strip()
        categoria = self.entries["categoria"].get().strip()
        
        exitoso, mensaje = self.service.actualizar_producto(
            original_codigo, codigo, nombre, categoria, cantidad, precio
        )
        
        if exitoso:
            messagebox.showinfo("Éxito", mensaje)
            self.clear_form()
            self.load_products()
            self.update_total_value()
        else:
            messagebox.showerror("Error", mensaje)
    
    def delete_product(self):
        """Eliminar un producto."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
            return
        
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este producto?"):
            return
        
        codigo = self.tree.item(selected[0])["values"][0]
        
        # Eliminar usando el servicio
        exitoso, mensaje = self.service.eliminar_producto(codigo)
        
        if exitoso:
            messagebox.showinfo("Éxito", mensaje)
            self.clear_form()
            self.load_products()
            self.update_total_value()
        else:
            messagebox.showerror("Error", mensaje)
    
    def clear_entries(self):
        """Limpiar solo los campos de entrada sin deseleccionar la tabla."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
    
    def clear_form(self):
        """Limpiar todos los campos del formulario y deseleccionar tabla."""
        self.clear_entries()
        
        # Deseleccionar en la tabla
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def on_select(self, event):
        """Manejar selección de producto en la tabla."""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Obtener valores del producto seleccionado
        values = self.tree.item(selected[0])["values"]
        
        # Limpiar solo los campos (sin deseleccionar)
        self.clear_entries()
        
        # Llenar formulario con valores seleccionados
        self.entries["codigo"].insert(0, values[0])
        self.entries["nombre"].insert(0, values[1])
        self.entries["categoria"].insert(0, values[2])
        self.entries["cantidad"].insert(0, values[3])
        # Remover el símbolo $ del precio
        precio = str(values[4]).replace("$", "")
        self.entries["precio_unitario"].insert(0, precio)
    
    def update_total_value(self):
        """Calcular y mostrar el valor total del inventario."""
        total = self.service.calcular_valor_total()
        self.total_label.config(text=f"◈ VALOR TOTAL DEL INVENTARIO: ${total:,.2f}")


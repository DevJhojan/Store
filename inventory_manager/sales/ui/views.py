"""Vista de la interfaz gráfica del módulo de Ventas."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List

from ...config.settings import Settings, COLORS
from ...ui.styles import StyleManager
from ...utils.validators import parse_numeric_field
from ..domain.models import Venta, ItemVenta
from ..services.venta_service import VentaService


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
        
        # Crear ventana Toplevel si el padre es Tk
        if isinstance(parent_window, tk.Tk):
            self.window = tk.Toplevel(parent_window)
        else:
            self.window = parent_window
        
        # Venta actual en proceso
        self.venta_actual = Venta()
        
        # Referencia al módulo de inventario (para notificaciones)
        self.inventory_gui_ref = None
        
        # Configurar ventana
        self.window.title("💰 Sistema de Ventas")
        self.window.geometry("1000x700")
        self.window.configure(bg=COLORS["bg_darkest"])
        self.window.resizable(True, True)
        
        # Manejar cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar productos disponibles
        self.load_available_products()
    
    def on_close(self):
        """Maneja el cierre de la ventana."""
        if self.venta_actual.items:
            if not messagebox.askyesno("Confirmar", 
                                       "Tiene items en el carrito. ¿Desea cancelar la venta?"):
                return
        self.window.destroy()
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz."""
        c = COLORS
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg=c["bg_darkest"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Título
        title_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Frame(title_frame, bg=c["red_primary"], height=2).pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="◆ SISTEMA DE GESTIÓN DE VENTAS ◆",
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
        
        tk.Frame(title_frame, bg=c["red_primary"], height=2).pack(fill=tk.X, pady=(10, 0))
        
        # Frame para búsqueda y selección de productos
        search_container = tk.Frame(main_frame, bg=c["red_dark"], padx=2, pady=2)
        search_container.pack(fill=tk.X, pady=(0, 15))
        
        search_frame = tk.Frame(search_container, bg=c["bg_dark"], padx=20, pady=15)
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_search_section(search_frame)
        
        # Frame para el carrito de compra
        cart_container = tk.Frame(main_frame, bg=c["red_dark"], padx=2, pady=2)
        cart_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        cart_frame = tk.Frame(cart_container, bg=c["bg_dark"])
        cart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_cart_section(cart_frame)
        
        # Frame para total y botones de acción
        action_container = tk.Frame(main_frame, bg=c["red_primary"], padx=2, pady=2)
        action_container.pack(fill=tk.X)
        
        action_frame = tk.Frame(action_container, bg=c["bg_dark"], padx=20, pady=15)
        action_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_action_section(action_frame)
    
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
            text="🔍 Buscar",
            command=self.buscar_producto,
            style="Secondary.TButton"
        )
        btn_buscar.pack(side=tk.LEFT, padx=(0, 20))
        
        # Combo para selección rápida
        tk.Label(
            search_row,
            text="O seleccionar:",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_SMALL),
            fg=c["text_secondary"],
            bg=c["bg_dark"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.product_combo = ttk.Combobox(
            search_row,
            state="readonly",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_NORMAL),
            width=30
        )
        self.product_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.product_combo.bind("<<ComboboxSelected>>", self.on_product_selected)
        
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
            text="➕ Agregar al Carrito",
            command=self.agregar_al_carrito,
            style="Accent.TButton"
        )
        btn_agregar.pack(side=tk.LEFT)
        
        # Variable para producto seleccionado
        self.producto_seleccionado = None
    
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
        
        # Frame para tabla
        table_frame = tk.Frame(parent, bg=c["bg_dark"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para items
        columns = ("codigo", "nombre", "cantidad", "precio", "subtotal")
        self.cart_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scrollbar.set
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
        scrollbar.config(command=self.cart_tree.yview)
        
        # Botón para remover item
        btn_remover = ttk.Button(
            parent,
            text="🗑️ Remover Item Seleccionado",
            command=self.remover_item,
            style="Secondary.TButton"
        )
        btn_remover.pack(anchor="w", padx=5, pady=5)
    
    def create_action_section(self, parent: tk.Frame):
        """Crear la sección de acciones y total."""
        c = COLORS
        
        # Frame para botones y total
        action_row = tk.Frame(parent, bg=c["bg_dark"])
        action_row.pack(fill=tk.X)
        
        # Botones
        btn_frame = tk.Frame(action_row, bg=c["bg_dark"])
        btn_frame.pack(side=tk.LEFT)
        
        btn_finalizar = ttk.Button(
            btn_frame,
            text="✅ Finalizar Venta",
            command=self.finalizar_venta,
            style="Accent.TButton"
        )
        btn_finalizar.pack(side=tk.LEFT, padx=5)
        
        btn_limpiar = ttk.Button(
            btn_frame,
            text="🔄 Nueva Venta",
            command=self.nueva_venta,
            style="Secondary.TButton"
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        # Total
        self.total_label = tk.Label(
            action_row,
            text="TOTAL: $0.00",
            font=(Settings.FONT_PRIMARY, Settings.FONT_SIZE_MEDIUM, "bold"),
            fg=c["success"],
            bg=c["bg_dark"]
        )
        self.total_label.pack(side=tk.RIGHT, padx=10)
    
    def load_available_products(self):
        """Cargar productos disponibles en el combo."""
        productos = self.service.obtener_productos_disponibles()
        productos_texto = [f"{p.codigo} - {p.nombre} (Stock: {p.cantidad})" for p in productos]
        self.product_combo["values"] = productos_texto
        self.productos_disponibles = {p.codigo: p for p in productos}
    
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
            messagebox.showwarning("Advertencia", "Ingrese un código de producto.")
            return
        
        producto = self.service.buscar_producto_por_codigo(codigo)
        if not producto:
            messagebox.showerror("Error", f"Producto con código '{codigo}' no encontrado.")
            self.limpiar_info_producto()
            return
        
        if producto.cantidad == 0:
            messagebox.showwarning("Advertencia", f"El producto '{producto.nombre}' no tiene stock disponible.")
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
        
        info_text = (
            f"Nombre: {producto.nombre} | "
            f"Categoría: {producto.categoria} | "
            f"Precio: ${producto.precio_unitario:.2f} | "
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
            messagebox.showwarning("Advertencia", "Seleccione un producto primero.")
            return
        
        # Validar cantidad
        cantidad_exitoso, cantidad, msg_cantidad = parse_numeric_field(
            self.cantidad_entry.get().strip(), int
        )
        if not cantidad_exitoso:
            messagebox.showerror("Error", f"Cantidad: {msg_cantidad}")
            return
        
        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
            return
        
        # Verificar stock disponible
        if cantidad > self.producto_seleccionado.cantidad:
            messagebox.showerror(
                "Error",
                f"Stock insuficiente. Disponible: {self.producto_seleccionado.cantidad}, "
                f"Solicitado: {cantidad}."
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
                        f"({self.producto_seleccionado.cantidad})."
                    )
                    return
                item.cantidad = nueva_cantidad_total
                self.actualizar_carrito()
                return
        
        # Agregar nuevo item
        item = ItemVenta(
            codigo_producto=self.producto_seleccionado.codigo,
            nombre_producto=self.producto_seleccionado.nombre,
            cantidad=cantidad,
            precio_unitario=self.producto_seleccionado.precio_unitario
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
        
        # Actualizar total
        total = self.venta_actual.calcular_total()
        self.total_label.config(text=f"TOTAL: ${total:,.2f}")
    
    def remover_item(self):
        """Remueve el item seleccionado del carrito."""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un item para remover.")
            return
        
        index = self.cart_tree.index(selected[0])
        self.venta_actual.remover_item(index)
        self.actualizar_carrito()
    
    def finalizar_venta(self):
        """Finaliza y registra la venta."""
        if not self.venta_actual.items:
            messagebox.showwarning("Advertencia", "El carrito está vacío.")
            return
        
        # Confirmar venta
        total = self.venta_actual.calcular_total()
        if not messagebox.askyesno(
            "Confirmar Venta",
            f"¿Confirmar venta por un total de ${total:,.2f}?"
        ):
            return
        
        # Registrar venta
        exitoso, mensaje, venta_id = self.service.registrar_venta(self.venta_actual)
        
        if exitoso:
            messagebox.showinfo("Éxito", f"{mensaje}\nID de Venta: {venta_id}")
            self.nueva_venta()
            # Recargar productos disponibles (stock actualizado)
            self.load_available_products()
            # Notificar al módulo de inventario si está abierto
            if self.inventory_gui_ref:
                self.inventory_gui_ref.refresh()
        else:
            messagebox.showerror("Error", mensaje)
    
    def nueva_venta(self):
        """Inicia una nueva venta (limpia el carrito)."""
        if self.venta_actual.items:
            if not messagebox.askyesno("Confirmar", "¿Desea cancelar la venta actual?"):
                return
        
        self.venta_actual = Venta()
        self.actualizar_carrito()
        self.limpiar_info_producto()
        self.codigo_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "1")
        self.load_available_products()


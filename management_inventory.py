import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class InventoryManager:
    """Sistema de gestión de inventarios con interfaz gráfica."""
    
    # Paleta de colores - Tema Dark con acentos rojos
    COLORS = {
        "bg_darkest": "#0a0a0a",      # Fondo principal (casi negro)
        "bg_dark": "#121212",          # Fondo secundario
        "bg_medium": "#1a1a1a",        # Fondo de elementos
        "bg_light": "#242424",         # Fondo hover
        "red_primary": "#dc0000",      # Rojo principal
        "red_bright": "#ff1a1a",       # Rojo brillante (hover)
        "red_dark": "#8b0000",         # Rojo oscuro
        "red_glow": "#ff0000",         # Rojo para bordes/glow
        "text_primary": "#ffffff",     # Texto principal
        "text_secondary": "#b0b0b0",   # Texto secundario
        "text_muted": "#666666",       # Texto apagado
        "success": "#00ff00",          # Verde para valores positivos
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Sistema de Gestión de Inventarios")
        self.root.geometry("950x650")
        self.root.configure(bg=self.COLORS["bg_darkest"])
        self.root.resizable(True, True)
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar base de datos
        self.init_database()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar productos existentes
        self.load_products()
        
        # Actualizar valor total
        self.update_total_value()
    
    def setup_styles(self):
        """Configurar estilos personalizados para la interfaz."""
        style = ttk.Style()
        style.theme_use("clam")
        
        c = self.COLORS
        
        # Estilo para Treeview
        style.configure(
            "Custom.Treeview",
            background=c["bg_dark"],
            foreground=c["text_primary"],
            fieldbackground=c["bg_dark"],
            rowheight=32,
            font=("Consolas", 10),
            borderwidth=0
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=c["red_dark"],
            foreground=c["text_primary"],
            font=("Consolas", 10, "bold"),
            borderwidth=1,
            relief="flat"
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", c["red_primary"])],
            foreground=[("selected", c["text_primary"])]
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", c["red_primary"])]
        )
        
        # Estilo para botones principales (rojo)
        style.configure(
            "Accent.TButton",
            background=c["red_primary"],
            foreground=c["text_primary"],
            font=("Consolas", 10, "bold"),
            padding=(18, 10),
            borderwidth=2
        )
        style.map(
            "Accent.TButton",
            background=[("active", c["red_bright"]), ("pressed", c["red_dark"])]
        )
        
        # Estilo para botones secundarios (oscuros con borde rojo)
        style.configure(
            "Secondary.TButton",
            background=c["bg_medium"],
            foreground=c["text_primary"],
            font=("Consolas", 10),
            padding=(18, 10),
            borderwidth=2
        )
        style.map(
            "Secondary.TButton",
            background=[("active", c["bg_light"]), ("pressed", c["bg_dark"])]
        )
        
        # Estilo para scrollbar
        style.configure(
            "Custom.Vertical.TScrollbar",
            background=c["bg_medium"],
            troughcolor=c["bg_dark"],
            borderwidth=0,
            arrowcolor=c["red_primary"]
        )
        style.map(
            "Custom.Vertical.TScrollbar",
            background=[("active", c["red_primary"])]
        )
    
    def init_database(self):
        """Inicializar la base de datos SQLite."""
        self.conn = sqlite3.connect("inventario.db")
        self.cursor = self.conn.cursor()
        
        # Crear tabla de productos si no existe
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                codigo TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL
            )
        """)
        self.conn.commit()
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz."""
        c = self.COLORS
        
        # Frame principal con borde rojo
        main_frame = tk.Frame(self.root, bg=c["bg_darkest"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Título con estilo cyberpunk
        title_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Línea decorativa superior
        tk.Frame(title_frame, bg=c["red_primary"], height=2).pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text="◆ SISTEMA DE GESTIÓN DE INVENTARIOS ◆",
            font=("Consolas", 18, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="[ Control Digital de Productos ]",
            font=("Consolas", 10),
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
            font=("Consolas", 14, "bold"),
            fg=c["success"],
            bg=c["bg_dark"]
        )
        self.total_label.pack()
    
    def create_form_fields(self, parent):
        """Crear los campos del formulario."""
        c = self.COLORS
        
        # Configurar grid
        for i in range(5):
            parent.columnconfigure(i * 2, weight=0)
            parent.columnconfigure(i * 2 + 1, weight=1)
        
        self.entries = {}
        
        label_style = {
            "font": ("Consolas", 10, "bold"),
            "fg": c["red_primary"],
            "bg": c["bg_dark"]
        }
        entry_style = {
            "font": ("Consolas", 11),
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
    
    def create_buttons(self, parent):
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
    
    def create_table(self, parent):
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
        
        widths = {"codigo": 100, "nombre": 200, "categoria": 120, "cantidad": 80, "precio_unitario": 100, "subtotal": 100}
        
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.tree.yview)
        
        # Evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def load_products(self):
        """Cargar productos desde la base de datos."""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener productos
        self.cursor.execute("SELECT * FROM productos")
        products = self.cursor.fetchall()
        
        # Insertar en tabla
        for product in products:
            codigo, nombre, categoria, cantidad, precio = product
            subtotal = cantidad * precio
            self.tree.insert("", tk.END, values=(
                codigo,
                nombre,
                categoria,
                cantidad,
                f"${precio:.2f}",
                f"${subtotal:.2f}"
            ))
    
    def add_product(self):
        """Agregar un nuevo producto."""
        # Validar campos
        if not self.validate_fields():
            return
        
        try:
            codigo = self.entries["codigo"].get().strip()
            nombre = self.entries["nombre"].get().strip()
            categoria = self.entries["categoria"].get().strip()
            cantidad = int(self.entries["cantidad"].get().strip())
            precio = float(self.entries["precio_unitario"].get().strip())
            
            # Verificar si el código ya existe
            self.cursor.execute("SELECT codigo FROM productos WHERE codigo = ?", (codigo,))
            if self.cursor.fetchone():
                messagebox.showerror("Error", "Ya existe un producto con ese código.")
                return
            
            # Insertar producto
            self.cursor.execute(
                "INSERT INTO productos VALUES (?, ?, ?, ?, ?)",
                (codigo, nombre, categoria, cantidad, precio)
            )
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
            self.clear_form()
            self.load_products()
            self.update_total_value()
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número entero y precio un número decimal.")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", str(e))
    
    def update_product(self):
        """Actualizar un producto existente."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para actualizar.")
            return
        
        if not self.validate_fields():
            return
        
        try:
            codigo = self.entries["codigo"].get().strip()
            nombre = self.entries["nombre"].get().strip()
            categoria = self.entries["categoria"].get().strip()
            cantidad = int(self.entries["cantidad"].get().strip())
            precio = float(self.entries["precio_unitario"].get().strip())
            
            # Obtener código original del producto seleccionado
            original_codigo = str(self.tree.item(selected[0])["values"][0])
            
            # Si el código cambió, verificar que no exista
            if codigo != original_codigo:
                self.cursor.execute("SELECT codigo FROM productos WHERE codigo = ?", (codigo,))
                if self.cursor.fetchone():
                    messagebox.showerror("Error", "Ya existe un producto con ese código.")
                    return
            
            # Actualizar producto
            self.cursor.execute("""
                UPDATE productos 
                SET codigo = ?, nombre = ?, categoria = ?, cantidad = ?, precio_unitario = ?
                WHERE codigo = ?
            """, (codigo, nombre, categoria, cantidad, precio, original_codigo))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
            self.clear_form()
            self.load_products()
            self.update_total_value()
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número entero y precio un número decimal.")
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", str(e))
    
    def delete_product(self):
        """Eliminar un producto."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
            return
        
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este producto?"):
            return
        
        try:
            codigo = self.tree.item(selected[0])["values"][0]
            
            self.cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
            self.conn.commit()
            
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            self.clear_form()
            self.load_products()
            self.update_total_value()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", str(e))
    
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
    
    def validate_fields(self):
        """Validar que todos los campos estén llenos."""
        for key, entry in self.entries.items():
            if not entry.get().strip():
                field_names = {
                    "codigo": "Código",
                    "nombre": "Nombre",
                    "categoria": "Categoría",
                    "cantidad": "Cantidad",
                    "precio_unitario": "Precio Unitario"
                }
                messagebox.showerror("Error", f"El campo '{field_names[key]}' es obligatorio.")
                entry.focus()
                return False
        return True
    
    def update_total_value(self):
        """Calcular y mostrar el valor total del inventario."""
        self.cursor.execute("SELECT SUM(cantidad * precio_unitario) FROM productos")
        result = self.cursor.fetchone()[0]
        total = result if result else 0
        self.total_label.config(text=f"◈ VALOR TOTAL DEL INVENTARIO: ${total:,.2f}")
    
    def __del__(self):
        """Cerrar conexión a la base de datos al destruir el objeto."""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Función principal para ejecutar la aplicación."""
    root = tk.Tk()
    app = InventoryManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()


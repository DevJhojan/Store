"""Vista de la interfaz gráfica del módulo de Inventarios."""
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional

from ..config.settings import COLORS
from ..services.inventory_service import InventoryService
from ..ui.styles import StyleManager
from .widgets.lateral_panel import create_lateral_panel
from .widgets.form_widgets import create_form_widgets
from .widgets.button_bar import create_button_bar
from .widgets.table_widgets import create_table_widget
from .widgets.summary_widget import create_summary_widget
from .handlers.crud_handlers import agregar_producto, actualizar_producto, eliminar_producto
from .handlers.form_handlers import clear_form
from .handlers.table_handlers import refresh_table, on_producto_seleccionado


class InventoryGUI:
    """Interfaz gráfica del módulo de gestión de inventarios."""
    
    def __init__(self, parent_window, service: Optional[InventoryService] = None):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            parent_window: Ventana padre (Tk o Frame)
            service: Servicio de inventario (si None, se crea uno nuevo)
        """
        self.parent = parent_window
        self.service = service or InventoryService()
        
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
        else:
            # Si es Frame, solo configurar el fondo
            self.window.configure(bg=COLORS["bg_darkest"])
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Diccionario de campos de entrada
        self.entries: Dict[str, tk.Entry] = {}
        self.ganancia_entry: Optional[tk.Entry] = None
        self.codigo_lateral_entry: Optional[tk.Entry] = None
        
        # Producto seleccionado para actualizar
        self.producto_seleccionado: Optional[str] = None
        
        # Referencias a widgets
        self.tree = None
        self.summary_labels: Dict[str, tk.Label] = {}
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar productos
        self.refresh()
    
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
        lateral_entries = create_lateral_panel(main_frame)
        self.entries.update(lateral_entries)
        self.codigo_lateral_entry = lateral_entries["codigo_lateral"]
        
        # ========== FORMULARIO PRINCIPAL (Parte Superior) ==========
        form_entries, self.ganancia_entry = create_form_widgets(
            main_frame,
            on_calculo_change=self.on_calculo_cambio
        )
        self.entries.update(form_entries)
        
        # ========== BARRA DE BOTONES ==========
        create_button_bar(
            main_frame,
            on_add=self.agregar_producto,
            on_update=self.actualizar_producto,
            on_delete=self.eliminar_producto,
            on_clear=self.limpiar_formulario
        )
        
        # ========== SECCIÓN INFERIOR (Tabla y Resumen) ==========
        bottom_frame = tk.Frame(main_frame, bg=c["bg_darkest"])
        bottom_frame.grid(row=2, column=1, sticky="nsew", padx=0, pady=0)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=3)  # Tabla expandible
        bottom_frame.grid_rowconfigure(1, weight=0)  # Resumen fijo
        
        # Tabla de datos
        self.tree = create_table_widget(bottom_frame)
        self.tree.bind("<<TreeviewSelect>>", self._on_producto_seleccionado_event)
        
        # Resumen total
        self.summary_labels = create_summary_widget(bottom_frame, self.recalcular)
        
        # Generar código inicial
        self.limpiar_formulario()
    
    def _on_producto_seleccionado_event(self, event):
        """Wrapper para el evento de selección de producto."""
        self.producto_seleccionado = on_producto_seleccionado(
            event,
            self.tree,
            self.service,
            self.entries,
            self.ganancia_entry,
            self.codigo_lateral_entry
        )
    
    def on_calculo_cambio(self, event=None):
        """Recalcula los valores cuando cambian cantidad, precio o ganancia."""
        # Este método puede usarse para mostrar cálculos en tiempo real si se desea
        # Por ahora, los cálculos se hacen al guardar y mostrar en la tabla
        pass
    
    def recalcular(self):
        """Recalcula todos los valores de la tabla y el resumen."""
        self.refresh()
        messagebox.showinfo("Recalculado", "Los valores han sido recalculados correctamente.", parent=self.window)
    
    def agregar_producto(self):
        """Agrega un nuevo producto al inventario."""
        agregar_producto(
            self.window,
            self.entries,
            self.ganancia_entry,
            self.tree,
            self.codigo_lateral_entry,
            self.service,
            self.refresh
        )
    
    def actualizar_producto(self):
        """Actualiza un producto existente."""
        self.producto_seleccionado = actualizar_producto(
            self.window,
            self.producto_seleccionado,
            self.entries,
            self.ganancia_entry,
            self.tree,
            self.codigo_lateral_entry,
            self.service,
            self.refresh
        )
    
    def eliminar_producto(self):
        """Elimina un producto del inventario."""
        self.producto_seleccionado = eliminar_producto(
            self.window,
            self.producto_seleccionado,
            self.entries,
            self.ganancia_entry,
            self.tree,
            self.codigo_lateral_entry,
            self.service,
            self.refresh
        )
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario."""
        clear_form(
            self.entries,
            self.ganancia_entry,
            self.codigo_lateral_entry,
            self.tree,
            self.service
        )
        self.producto_seleccionado = None
    
    def refresh(self):
        """Actualiza la tabla y el resumen."""
        refresh_table(self.tree, self.service, self.summary_labels)


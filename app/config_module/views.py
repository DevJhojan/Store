"""Vista de la interfaz gráfica del módulo de Configuración."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from ..config.settings import COLORS, set_theme
from ..ui.styles import StyleManager
from .services.categoria_service import CategoriaService
from .services.theme_service import ThemeService
from .services.tienda_service import TiendaService
from .widgets.theme_widget import create_theme_widget
from .widgets.tienda_widget import create_tienda_widget
from .widgets.categoria_widget import (
    create_categoria_form_widget,
    create_categoria_buttons_widget,
    create_categoria_table_widget
)
from .handlers.categoria_handlers import (
    refresh_categoria_table,
    on_categoria_selected,
    agregar_categoria,
    actualizar_categoria,
    eliminar_categoria,
    limpiar_formulario_categoria
)
from .handlers.tienda_handlers import (
    cargar_informacion_tienda,
    guardar_informacion_tienda
)


class ConfigGUI:
    """Interfaz gráfica del módulo de configuración."""
    
    def __init__(self, parent_window, categoria_service: Optional[CategoriaService] = None):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            parent_window: Ventana padre (Tk o Frame)
            categoria_service: Servicio de categorías (si None, se crea uno nuevo)
        """
        self.parent = parent_window
        self.categoria_service = categoria_service or CategoriaService()
        self.theme_service = ThemeService()
        self.tienda_service = TiendaService()
        
        # Guardar referencia al root de la aplicación para actualizar tema
        self.app_root = None
        if isinstance(parent_window, tk.Frame):
            # Si es un Frame, buscar el root subiendo por la jerarquía
            widget = parent_window
            while widget and not isinstance(widget, tk.Tk):
                widget = widget.master if hasattr(widget, 'master') else None
            self.app_root = widget
        elif isinstance(parent_window, tk.Tk):
            self.app_root = parent_window
        
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
            self.window.title("⚙️ Configuración")
            self.window.configure(bg=COLORS["bg_darkest"])
            self.window.resizable(True, True)
        else:
            # Si es Frame, solo configurar el fondo
            self.window.configure(bg=COLORS["bg_darkest"])
        
        # Configurar estilos
        self.style_manager = StyleManager()
        
        # Referencias a widgets
        self.categoria_seleccionada_id: Optional[int] = None
        self.form_widgets: Dict[str, tk.Widget] = {}
        self.categoria_tree = None
        self.tienda_widgets: Dict[str, tk.Widget] = {}
        self.scrollable_frame = None
        self.canvas = None
        
        # Cargar tema actual
        tema_actual = self.theme_service.obtener_tema_actual()
        set_theme(tema_actual)
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar categorías
        self.refresh_categorias()
        
        # Actualizar tema en el widget
        if hasattr(self, 'theme_widget') and hasattr(self.theme_widget, 'theme_combo'):
            self.theme_widget.theme_combo.set(tema_actual.capitalize())
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        from tkinter import ttk
        c = COLORS
        
        # Canvas principal para scrollbar
        self.canvas = tk.Canvas(
            self.window,
            bg=c["bg_darkest"],
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar vertical estilizada
        v_scrollbar = ttk.Scrollbar(
            self.window,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            style="Custom.Vertical.TScrollbar"
        )
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar scrollbar con canvas
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Frame scrollable dentro del canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=c["bg_darkest"], padx=10, pady=10)
        
        # Crear ventana en el canvas para el frame scrollable
        canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        
        # Configurar scroll del canvas
        def on_frame_configure(event):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            except tk.TclError:
                pass
        
        def on_canvas_configure(event):
            try:
                if self.canvas.winfo_exists():
                    canvas_width = event.width
                    self.canvas.itemconfig(canvas_window, width=canvas_width)
            except tk.TclError:
                pass
        
        # Habilitar scroll con rueda del mouse (Windows/Mac)
        def on_mousewheel(event):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        # Habilitar scroll con rueda del mouse (Linux)
        def on_button4(event):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(-1, "units")
            except tk.TclError:
                pass
        
        def on_button5(event):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(1, "units")
            except tk.TclError:
                pass
        
        # Bind eventos
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.canvas.bind_all("<Button-4>", on_button4)
        self.canvas.bind_all("<Button-5>", on_button5)
        
        # Usar scrollable_frame como main_frame
        main_frame = self.scrollable_frame
        
        # Título
        from ..config.settings import Settings
        title_label = tk.Label(
            main_frame,
            text="⚙️ CONFIGURACIÓN",
            font=(Settings.FONT_PRIMARY, 18, "bold"),
            fg=c["red_primary"],
            bg=c["bg_darkest"],
            pady=10
        )
        title_label.pack()
        
        # Separador visual
        separator1 = tk.Frame(main_frame, bg=c["bg_medium"], height=2)
        separator1.pack(fill=tk.X, padx=15, pady=10)
        
        # Sección de información de tienda
        self.tienda_widgets = create_tienda_widget(main_frame, self.guardar_informacion_tienda)
        cargar_informacion_tienda(self.tienda_widgets, self.tienda_service)
        
        # Separador visual
        separator2 = tk.Frame(main_frame, bg=c["bg_medium"], height=2)
        separator2.pack(fill=tk.X, padx=15, pady=10)
        
        # Sección de tema
        self.theme_widget = create_theme_widget(main_frame, self.on_theme_change)
        
        # Separador visual
        separator3 = tk.Frame(main_frame, bg=c["bg_medium"], height=2)
        separator3.pack(fill=tk.X, padx=15, pady=10)
        
        # Sección de categorías
        categoria_section = tk.Frame(main_frame, bg=c["bg_darkest"])
        categoria_section.pack(fill=tk.X, pady=(0, 15))
        
        # Formulario de categorías
        self.form_widgets = create_categoria_form_widget(categoria_section)
        
        # Botones de categorías
        create_categoria_buttons_widget(
            categoria_section,
            on_add=self.agregar_categoria,
            on_update=self.actualizar_categoria,
            on_delete=self.eliminar_categoria,
            on_clear=self.limpiar_formulario
        )
        
        # Tabla de categorías
        self.categoria_tree = create_categoria_table_widget(categoria_section)
        self.categoria_tree.bind("<<TreeviewSelect>>", self._on_categoria_selected_event)
        
        # Actualizar scrollregion inicial después de que todos los widgets estén creados
        def update_scrollregion():
            try:
                self.window.update_idletasks()
                if self.canvas.winfo_exists():
                    bbox = self.canvas.bbox("all")
                    if bbox:
                        self.canvas.configure(scrollregion=bbox)
            except tk.TclError:
                pass
        
        # Actualizar después de un breve delay para asegurar que todos los widgets estén renderizados
        self.window.after(100, update_scrollregion)
        
        # Aplicar tema actual al inicializar
        self.apply_theme()
    
    def apply_theme(self):
        """Aplica el tema actual a todos los widgets del módulo."""
        from .utils.theme_updater import update_application_theme
        from ..config.settings import COLORS
        
        # Recargar StyleManager con el tema actual
        self.style_manager = StyleManager()
        
        # Actualizar todos los widgets del módulo
        update_application_theme(self.window, self.style_manager)
        
        # Actualizar manualmente el estilo del Combobox de tema si existe
        if hasattr(self, 'theme_widget') and hasattr(self.theme_widget, 'theme_combo'):
            try:
                from tkinter import ttk
                style = ttk.Style()
                style.configure("TCombobox", fieldbackground=COLORS["bg_medium"], foreground=COLORS["text_primary"])
            except:
                pass
    
    def _on_categoria_selected_event(self, event):
        """Wrapper para el evento de selección de categoría."""
        self.categoria_seleccionada_id = on_categoria_selected(
            event,
            self.categoria_tree,
            self.categoria_service,
            self.form_widgets
        )
    
    def on_theme_change(self, theme_name: str):
        """Maneja el cambio de tema."""
        from tkinter import messagebox
        from .utils.theme_updater import update_application_theme
        
        # Convertir nombre a minúsculas
        theme = theme_name.lower()
        
        # Cambiar tema
        exito, mensaje = self.theme_service.cambiar_tema(theme)
        
        if exito:
            # Aplicar tema globalmente
            set_theme(theme)
            
            # Recargar estilos
            self.style_manager = StyleManager()
            
            # Obtener el root de la aplicación para actualizar tema
            root_to_update = self.app_root
            if not root_to_update:
                # Si no tenemos app_root, intentar encontrarlo
                root_to_update = self.window
                while hasattr(root_to_update, 'master') and root_to_update.master:
                    root_to_update = root_to_update.master
                if not isinstance(root_to_update, tk.Tk):
                    root_to_update = self.window
            
            # Actualizar tema de toda la aplicación
            if root_to_update:
                update_application_theme(root_to_update, self.style_manager)
            
            # También recargar estilos del main_window si existe
            if hasattr(self.parent, 'style_manager'):
                self.parent.style_manager = StyleManager()
                # Actualizar también desde el main_window
                if hasattr(self.parent, 'root'):
                    update_application_theme(self.parent.root, self.parent.style_manager)
            
            messagebox.showinfo(
                "Tema",
                f"Tema cambiado a '{theme_name}' exitosamente.",
                parent=self.window
            )
        else:
            messagebox.showerror("Error", mensaje, parent=self.window)
    
    def agregar_categoria(self):
        """Agrega una nueva categoría."""
        agregar_categoria(
            self.window,
            self.form_widgets,
            self.categoria_service,
            self.refresh_categorias
        )
        self.categoria_seleccionada_id = None
    
    def actualizar_categoria(self):
        """Actualiza una categoría existente."""
        self.categoria_seleccionada_id = actualizar_categoria(
            self.window,
            self.categoria_seleccionada_id,
            self.form_widgets,
            self.categoria_service,
            self.refresh_categorias
        )
    
    def eliminar_categoria(self):
        """Elimina una categoría."""
        self.categoria_seleccionada_id = eliminar_categoria(
            self.window,
            self.categoria_seleccionada_id,
            self.form_widgets,
            self.categoria_service,
            self.refresh_categorias
        )
    
    def limpiar_formulario(self):
        """Limpia el formulario de categorías."""
        limpiar_formulario_categoria(self.form_widgets, self.categoria_tree)
        self.categoria_seleccionada_id = None
    
    def refresh_categorias(self):
        """Actualiza la tabla de categorías."""
        refresh_categoria_table(self.categoria_tree, self.categoria_service)
    
    def obtener_categorias(self):
        """Obtiene todas las categorías."""
        return self.categoria_service.obtener_todas_las_categorias()
    
    def guardar_informacion_tienda(self):
        """Guarda la información de la tienda."""
        guardar_informacion_tienda(
            self.window,
            self.tienda_widgets,
            self.tienda_service
        )


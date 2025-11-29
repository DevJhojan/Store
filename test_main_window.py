"""Script de prueba para verificar que la ventana principal muestre ambas tarjetas."""
import sys
import tkinter as tk

sys.path.insert(0, '/home/devjdtp/Proyectos/Store')

try:
    from inventory_manager.main_window import MainWindow
    
    print("="*60)
    print("PROBANDO VENTANA PRINCIPAL")
    print("="*60)
    print()
    print("✓ Importaciones correctas")
    print("✓ Creando ventana principal...")
    
    root = tk.Tk()
    app = MainWindow(root)
    
    print("✓ Ventana principal creada")
    print()
    print("VERIFICANDO COMPONENTES:")
    print("  - Tarjeta de Inventarios: ", end="")
    
    # Buscar si existe el botón de inventario
    for widget in root.winfo_children():
        for child in widget.winfo_children():
            for subchild in child.winfo_children():
                if hasattr(subchild, 'winfo_children'):
                    for item in subchild.winfo_children():
                        if isinstance(item, tk.Label):
                            if "INVENTARIOS" in item.cget("text"):
                                print("✅ ENCONTRADA")
                                break
                        elif isinstance(item, tk.Frame):
                            for btn in item.winfo_children():
                                if isinstance(btn, tk.ttk.Button):
                                    if hasattr(btn, 'cget') and btn.cget('text') == "▶ Abrir Módulo":
                                        print("✅ BOTÓN ENCONTRADO")
    
    print("  - Tarjeta de Ventas: ", end="")
    # Buscar si existe el botón de ventas
    for widget in root.winfo_children():
        for child in widget.winfo_children():
            for subchild in child.winfo_children():
                if hasattr(subchild, 'winfo_children'):
                    for item in subchild.winfo_children():
                        if isinstance(item, tk.Label):
                            if "VENTAS" in item.cget("text"):
                                print("✅ ENCONTRADA")
                                break
    
    print()
    print("="*60)
    print("VENTANA LISTA - Deberías ver ambas tarjetas:")
    print("  1. 📦 GESTIÓN DE INVENTARIOS")
    print("  2. 💰 GESTIÓN DE VENTAS")
    print("="*60)
    print()
    print("Cerrando ventana de prueba en 3 segundos...")
    
    root.after(3000, root.destroy)
    root.mainloop()
    
    print("✓ Prueba completada")
    
except Exception as e:
    import traceback
    print(f"✗ ERROR: {e}")
    traceback.print_exc()


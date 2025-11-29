"""Punto de entrada principal para la aplicación de gestión de inventarios."""
import tkinter as tk

from inventory_manager.ui import InventoryManagerGUI


def main():
    """Función principal para ejecutar la aplicación."""
    root = tk.Tk()
    app = InventoryManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


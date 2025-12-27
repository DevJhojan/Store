"""Punto de entrada principal para la aplicación de gestión."""
import tkinter as tk

from app.main_window import MainWindow


def main():
    """Función principal para ejecutar la aplicación."""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()


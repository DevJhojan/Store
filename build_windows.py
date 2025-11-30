"""
Script para construir el ejecutable de Windows (.exe)
Requiere: pip install pyinstaller
"""
import os
import sys
import subprocess
import shutil

def build_windows_exe():
    """Construye el ejecutable para Windows."""
    print("🔨 Construyendo ejecutable para Windows...")
    
    # Verificar que PyInstaller esté instalado
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Limpiar builds anteriores
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("main.spec"):
        os.remove("main.spec")
    
    # Comando de PyInstaller
    # Usar el archivo .spec para mejor control
    cmd = [
        "pyinstaller",
        "--clean",
        "pyinstaller_windows.spec"
    ]
    
    print("📦 Ejecutando PyInstaller...")
    subprocess.check_call(cmd)
    
    print("✅ Ejecutable creado en: dist/StoreManagement.exe")
    print("📁 El archivo .exe está listo para distribuir")

if __name__ == "__main__":
    build_windows_exe()


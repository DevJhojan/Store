"""
Script para construir el ejecutable/paquete para Linux
Opciones: ejecutable standalone o paquete .deb
"""
import os
import sys
import subprocess
import shutil

def build_linux_executable():
    """Construye un ejecutable standalone para Linux usando PyInstaller."""
    print("🔨 Construyendo ejecutable para Linux...")
    
    # Verificar que PyInstaller esté instalado
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Verificar que el archivo .spec existe
    if not os.path.exists("pyinstaller_linux.spec"):
        print("❌ Archivo pyinstaller_linux.spec no encontrado.")
        print("💡 Creando archivo .spec...")
        # Crear el archivo .spec usando PyInstaller
        subprocess.check_call([
            "pyinstaller",
            "--name=StoreManagement",
            "--onefile",
            "--windowed",
            "--add-data=app:app",
            "--hidden-import=tkinter",
            "--hidden-import=sqlite3",
            "--hidden-import=reportlab",
            "--hidden-import=PIL",
            "--collect-all=tkinter",
            "--specpath=.",
            "main.py"
        ])
        # Renombrar el spec generado
        if os.path.exists("main.spec"):
            os.rename("main.spec", "pyinstaller_linux.spec")
    
    # Limpiar builds anteriores
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Comando de PyInstaller para Linux
    # Usar el archivo .spec para mejor control
    cmd = [
        "pyinstaller",
        "--clean",
        "pyinstaller_linux.spec"
    ]
    
    print("📦 Ejecutando PyInstaller...")
    subprocess.check_call(cmd)
    
    # Hacer ejecutable
    if os.path.exists("dist/StoreManagement"):
        os.chmod("dist/StoreManagement", 0o755)
        print("✅ Ejecutable creado en: dist/StoreManagement")
        print("📁 El archivo está listo para distribuir")
    else:
        print("⚠️  El ejecutable no se creó correctamente. Revisa los errores arriba.")

def build_deb_package():
    """Construye un paquete .deb para distribuciones basadas en Debian."""
    print("🔨 Construyendo paquete .deb...")
    
    # Crear estructura de directorios para el paquete .deb
    deb_dir = "deb_package"
    if os.path.exists(deb_dir):
        shutil.rmtree(deb_dir)
    
    os.makedirs(f"{deb_dir}/DEBIAN")
    os.makedirs(f"{deb_dir}/usr/bin")
    os.makedirs(f"{deb_dir}/usr/share/applications")
    os.makedirs(f"{deb_dir}/usr/share/store-management")
    
    # Primero construir el ejecutable
    build_linux_executable()
    
    # Copiar el ejecutable
    if os.path.exists("dist/StoreManagement"):
        shutil.copy("dist/StoreManagement", f"{deb_dir}/usr/bin/store-management")
        os.chmod(f"{deb_dir}/usr/bin/store-management", 0o755)
    
    # Crear archivo de control para el paquete .deb
    control_content = """Package: store-management
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-tk, python3-pil
Maintainer: Store Development Team <dev@store.com>
Description: Sistema de Gestión de Inventarios y Ventas
 Sistema completo de gestión con módulos de Inventarios,
 Ventas y Cierre de Caja, con interfaz gráfica usando tkinter.
"""
    
    with open(f"{deb_dir}/DEBIAN/control", "w") as f:
        f.write(control_content)
    
    # Crear archivo .desktop para el menú de aplicaciones
    desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Store Management
Comment=Sistema de Gestión de Inventarios y Ventas
Exec=store-management
Icon=store-management
Terminal=false
Categories=Office;Finance;
"""
    
    with open(f"{deb_dir}/usr/share/applications/store-management.desktop", "w") as f:
        f.write(desktop_content)
    
    # Construir el paquete .deb
    print("📦 Construyendo paquete .deb...")
    subprocess.check_call(["dpkg-deb", "--build", deb_dir, "store-management_1.0.0_amd64.deb"])
    
    print("✅ Paquete .deb creado: store-management_1.0.0_amd64.deb")
    print("💡 Para instalar: sudo dpkg -i store-management_1.0.0_amd64.deb")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Construir ejecutable o paquete para Linux")
    parser.add_argument("--deb", action="store_true", help="Construir paquete .deb")
    parser.add_argument("--executable", action="store_true", help="Construir solo ejecutable (default)")
    
    args = parser.parse_args()
    
    if args.deb:
        build_deb_package()
    else:
        build_linux_executable()


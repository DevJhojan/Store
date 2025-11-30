# 📦 Instrucciones para Construir Ejecutables

Este documento explica cómo generar los ejecutables para Windows y Linux.

## 🔧 Requisitos Previos

### Para Windows:
- Python 3.8 o superior
- pip (incluido con Python)

### Para Linux:
- Python 3.8 o superior
- pip3
- dpkg-deb (solo si quieres crear paquete .deb)

## 🪟 Construir Ejecutable para Windows (.exe)

### Opción 1: Usar el script batch (recomendado)
```bash
build.bat
```

### Opción 2: Usar el script Python
```bash
python build_windows.py
```

### Opción 3: Usar PyInstaller directamente
```bash
pip install pyinstaller
pyinstaller pyinstaller_windows.spec
```

El ejecutable se generará en: `dist/StoreManagement.exe`

## 🐧 Construir Ejecutable para Linux

### Opción 1: Ejecutable Standalone
```bash
./build.sh
```
o
```bash
python3 build_linux.py
```

### Opción 2: Paquete .deb (para distribuciones basadas en Debian)
```bash
./build.sh --deb
```
o
```bash
python3 build_linux.py --deb
```

El ejecutable se generará en: `dist/StoreManagement`
El paquete .deb se generará como: `store-management_1.0.0_amd64.deb`

## 📋 Instalación de Dependencias

Antes de construir, instala las dependencias:

```bash
pip install -r requirements.txt
pip install pyinstaller  # Para construir ejecutables
```

## 🎯 Notas Importantes

1. **Bases de datos**: Los ejecutables crearán las bases de datos (`inventario.db` y `Ventas.DB`) en el directorio donde se ejecute el programa.

2. **Facturas PDF**: Las facturas se guardarán en la carpeta `facturas/` relativa al ejecutable.

3. **Iconos**: Puedes agregar un icono personalizado editando los archivos `.spec` y agregando la ruta al icono.

4. **Tamaño del ejecutable**: Los ejecutables pueden ser grandes (50-100MB) porque incluyen Python y todas las dependencias.

## 🚀 Distribución

- **Windows**: Distribuye el archivo `StoreManagement.exe` junto con un README explicando cómo usarlo.
- **Linux**: 
  - Para ejecutable: Distribuye `StoreManagement` y asegúrate de que tenga permisos de ejecución (`chmod +x StoreManagement`)
  - Para .deb: Distribuye el archivo `.deb` y los usuarios pueden instalarlo con `sudo dpkg -i store-management_1.0.0_amd64.deb`


#!/bin/bash
# Script para construir ejecutables para Linux

echo "🔨 Construyendo ejecutables para Linux..."

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Instalar dependencias si es necesario
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Limpiar builds anteriores
rm -rf build dist *.spec

# Construir ejecutable
echo "📦 Construyendo ejecutable..."
pyinstaller --clean pyinstaller_linux.spec

# Hacer ejecutable
chmod +x dist/StoreManagement

echo "✅ Ejecutable creado en: dist/StoreManagement"
echo "📁 El archivo está listo para distribuir"

# Opción para construir .deb
if [ "$1" == "--deb" ]; then
    echo "📦 Construyendo paquete .deb..."
    python3 build_linux.py --deb
fi


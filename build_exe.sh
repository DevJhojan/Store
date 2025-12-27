#!/bin/bash
# Script para construir ejecutable .exe para Windows
# Nota: Para generar un .exe real, necesitas estar en Windows o usar Wine.
# Este script usa el archivo pyinstaller_windows.spec

echo "🔨 Construyendo ejecutable .exe para Windows..."

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

# Verificar que el archivo .spec existe
if [ ! -f "pyinstaller_windows.spec" ]; then
    echo "❌ Archivo pyinstaller_windows.spec no encontrado"
    exit 1
fi

# Limpiar builds anteriores (pero mantener los archivos .spec)
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist 2>/dev/null
# Solo eliminar main.spec si existe (puede ser generado automáticamente)
[ -f "main.spec" ] && rm -f main.spec

# Construir ejecutable usando el spec de Windows
echo "📦 Construyendo ejecutable .exe con PyInstaller..."
python3 -m PyInstaller --clean pyinstaller_windows.spec

# Verificar si se creó el ejecutable
if [ -f "dist/StoreManagement.exe" ]; then
    echo ""
    echo "✅ ¡Ejecutable creado exitosamente!"
    echo "📁 Ubicación: dist/StoreManagement.exe"
    echo "📦 El archivo .exe está listo para distribuir"
    ls -lh dist/StoreManagement.exe
elif [ -f "dist/StoreManagement" ]; then
    echo ""
    echo "⚠️  Se creó un ejecutable, pero no es .exe (probablemente porque estás en Linux)"
    echo "📁 Ubicación: dist/StoreManagement"
    echo "💡 Para generar un .exe real, ejecuta este script en Windows o usa Wine"
    ls -lh dist/StoreManagement
else
    echo ""
    echo "❌ Error: No se pudo crear el ejecutable"
    echo "🔍 Revisa los mensajes de error arriba"
    exit 1
fi

echo ""
echo "🎉 Proceso completado"


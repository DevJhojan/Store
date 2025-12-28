#!/bin/bash
# Script para construir ejecutable .exe para Windows que funciona en Linux con Wine
# Requisitos: Wine, Python para Windows (instalado en Wine)
# 
# Uso: ./build_exe_wine.sh
# 
# Si Python no está instalado en Wine, el script te ofrecerá ejecutar
# install_python_wine.sh para instalarlo automáticamente.
#
# El .exe generado funcionará tanto en Windows como en Linux con Wine.

echo "🍷 Construyendo ejecutable .exe para Windows (compatible con Wine)..."
echo "   Este .exe funcionará tanto en Windows como en Linux con Wine"
echo ""

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que Wine esté instalado
if ! command -v wine &> /dev/null; then
    echo -e "${RED}❌ Wine no está instalado${NC}"
    echo "Instala Wine con: sudo apt install wine (o equivalente según tu distribución)"
    exit 1
fi

echo -e "${GREEN}✅ Wine detectado${NC}"
echo ""

# Verificar si Python está instalado en Wine
echo "🔍 Verificando Python en Wine..."
if ! wine python --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python no está instalado en Wine${NC}"
    echo ""
    echo "Para instalar Python en Wine, tienes dos opciones:"
    echo ""
    echo -e "${GREEN}Opción 1 (Recomendada - Automática):${NC}"
    echo "  ./install_python_wine.sh"
    echo "  Este script descarga e instala Python automáticamente"
    echo ""
    echo -e "${GREEN}Opción 2 (Manual):${NC}"
    echo "  1. Descarga Python para Windows desde: https://www.python.org/downloads/"
    echo "  2. Ejecuta: wine /ruta/al/python-installer.exe"
    echo "  3. Durante la instalación, marca 'Add Python to PATH'"
    echo ""
    echo -e "${YELLOW}¿Deseas ejecutar el instalador automático ahora? (s/n):${NC} "
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        if [ -f "install_python_wine.sh" ]; then
            echo ""
            echo "Ejecutando instalador automático..."
            ./install_python_wine.sh
            echo ""
            # Verificar nuevamente después de la instalación
            if ! wine python --version &> /dev/null; then
                echo -e "${RED}❌ La instalación no fue exitosa${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ No se encontró install_python_wine.sh${NC}"
            echo "Por favor, instala Python manualmente siguiendo la Opción 2"
            exit 1
        fi
    else
        echo "Por favor, instala Python antes de continuar."
        exit 1
    fi
else
    PYTHON_VERSION=$(wine python --version 2>&1)
    echo -e "${GREEN}✅ $PYTHON_VERSION detectado en Wine${NC}"
fi
echo ""

# Verificar si pip está disponible en Wine
echo "🔍 Verificando pip en Wine..."
if ! wine python -m pip --version &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip no está disponible en Wine${NC}"
    echo "Instalando pip..."
    wine python -m ensurepip --upgrade || {
        echo -e "${RED}❌ Error al instalar pip${NC}"
        exit 1
    }
fi
echo -e "${GREEN}✅ pip disponible en Wine${NC}"
echo ""

# Instalar dependencias del proyecto en Wine
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependencias del proyecto en Wine..."
    echo "   (Esto puede tomar varios minutos...)"
    wine python -m pip install -r requirements.txt || {
        echo -e "${YELLOW}⚠️  Algunas dependencias no se pudieron instalar, continuando...${NC}"
    }
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
    echo ""
fi

# Verificar PyInstaller en Wine
echo "🔍 Verificando PyInstaller en Wine..."
if ! wine python -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PyInstaller no está instalado en Wine${NC}"
    echo "Instalando PyInstaller..."
    wine python -m pip install pyinstaller || {
        echo -e "${RED}❌ Error al instalar PyInstaller${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ PyInstaller instalado${NC}"
else
    echo -e "${GREEN}✅ PyInstaller detectado${NC}"
fi
echo ""

# Verificar que el archivo .spec existe
if [ ! -f "pyinstaller_windows.spec" ]; then
    echo -e "${RED}❌ Archivo pyinstaller_windows.spec no encontrado${NC}"
    exit 1
fi

# Obtener directorio del proyecto
PROJECT_DIR=$(pwd)

# Limpiar builds anteriores (pero mantener el spec de Windows)
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist 2>/dev/null || true
# Solo eliminar main.spec si existe (puede ser generado automáticamente)
[ -f "main.spec" ] && rm -f main.spec
echo ""

# Construir ejecutable usando PyInstaller en Wine
echo "📦 Construyendo ejecutable .exe con PyInstaller en Wine..."
echo "   (Esto puede tomar varios minutos...)"
echo ""

# Convertir ruta del spec file a formato Windows para Wine
SPEC_FILE="$PROJECT_DIR/pyinstaller_windows.spec"
SPEC_FILE_WIN=$(winepath -w "$SPEC_FILE" 2>/dev/null || echo "$SPEC_FILE" | sed 's/\//\\/g')

# Ejecutar PyInstaller a través de Wine usando el spec file
cd "$PROJECT_DIR"
echo "Ejecutando: wine python -m PyInstaller --clean \"$SPEC_FILE_WIN\""
echo ""

# Capturar el exit code de PyInstaller correctamente
set +e  # No salir en error para poder manejar el exit code
wine python -m PyInstaller --clean "$SPEC_FILE_WIN" 2>&1 | grep -v "^wine:.*err:" | grep -v "^fixme:"
PYINSTALLER_EXIT=${PIPESTATUS[0]}
set -e  # Volver a activar exit en error

if [ $PYINSTALLER_EXIT -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Intento con --clean falló, intentando sin --clean...${NC}"
    echo ""
    set +e
    wine python -m PyInstaller "$SPEC_FILE_WIN" 2>&1 | grep -v "^wine:.*err:" | grep -v "^fixme:"
    PYINSTALLER_EXIT=${PIPESTATUS[0]}
    set -e
    
    if [ $PYINSTALLER_EXIT -ne 0 ]; then
        echo ""
        echo -e "${RED}❌ PyInstaller falló (exit code: $PYINSTALLER_EXIT)${NC}"
        echo "🔍 Revisa los mensajes de error arriba para más detalles"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}✅ PyInstaller completado${NC}"
echo ""

# Verificar si se creó el ejecutable
if [ -f "dist/StoreManagement.exe" ]; then
    echo ""
    echo -e "${GREEN}✅ ¡Ejecutable .exe creado exitosamente!${NC}"
    echo ""
    echo "📁 Ubicación: $(pwd)/dist/StoreManagement.exe"
    EXE_SIZE=$(du -h dist/StoreManagement.exe | cut -f1)
    echo "📦 Tamaño: $EXE_SIZE"
    echo ""
    echo "🍷 Para ejecutar en Linux con Wine:"
    echo "   wine dist/StoreManagement.exe"
    echo ""
    echo "💡 También puedes crear un script launcher:"
    echo "   cat > StoreManagement.sh << 'EOF'"
    echo "   #!/bin/bash"
    echo "   cd \"\$(dirname \"\$0\")\""
    echo "   wine dist/StoreManagement.exe \"\$@\""
    echo "   EOF"
    echo "   chmod +x StoreManagement.sh"
    echo ""
elif [ -f "dist/StoreManagement" ]; then
    echo -e "${YELLOW}⚠️  Se creó un ejecutable, pero no es .exe${NC}"
    echo "   Esto probablemente significa que PyInstaller no se ejecutó correctamente en Wine"
    echo "   Revisa los mensajes de error arriba"
    exit 1
else
    echo -e "${RED}❌ Error: No se pudo crear el ejecutable${NC}"
    echo "🔍 Revisa los mensajes de error arriba"
    exit 1
fi

echo -e "${GREEN}🎉 Proceso completado${NC}"

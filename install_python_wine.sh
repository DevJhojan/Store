#!/bin/bash
# Script auxiliar para instalar Python en Wine
# Este script descarga e instala Python para Windows en Wine

echo "🐍 Instalador de Python para Wine"
echo ""

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que Wine esté instalado
if ! command -v wine &> /dev/null; then
    echo -e "${RED}❌ Wine no está instalado${NC}"
    echo "Instala Wine primero con: sudo apt install wine"
    exit 1
fi

echo -e "${GREEN}✅ Wine detectado: $(wine --version)${NC}"
echo ""

# Versión de Python a instalar (puedes cambiar esto)
PYTHON_VERSION="3.9.13"
PYTHON_FULL_VERSION="python-${PYTHON_VERSION}-amd64"
PYTHON_INSTALLER="${PYTHON_FULL_VERSION}.exe"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_INSTALLER}"

# Directorio temporal para descargas
DOWNLOAD_DIR="$HOME/.cache/wine-python-installer"
mkdir -p "$DOWNLOAD_DIR"

# Verificar si Python ya está instalado
if wine python --version &> /dev/null; then
    EXISTING_VERSION=$(wine python --version 2>&1)
    echo -e "${GREEN}✅ Python ya está instalado en Wine: $EXISTING_VERSION${NC}"
    echo ""
    read -p "¿Deseas reinstalar Python? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        echo "Instalación cancelada."
        exit 0
    fi
fi

echo -e "${BLUE}📥 Descargando Python ${PYTHON_VERSION} para Windows...${NC}"
echo "URL: $PYTHON_URL"
echo ""

# Descargar Python
cd "$DOWNLOAD_DIR"
if [ -f "$PYTHON_INSTALLER" ]; then
    echo -e "${YELLOW}⚠️  El instalador ya existe en: $DOWNLOAD_DIR/$PYTHON_INSTALLER${NC}"
    read -p "¿Deseas descargarlo nuevamente? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        echo "Descargando..."
        wget -c "$PYTHON_URL" -O "$PYTHON_INSTALLER" || {
            echo -e "${RED}❌ Error al descargar Python${NC}"
            exit 1
        }
    fi
else
    echo "Descargando..."
    wget -c "$PYTHON_URL" -O "$PYTHON_INSTALLER" || {
        echo -e "${RED}❌ Error al descargar Python${NC}"
        exit 1
    }
fi

INSTALLER_PATH="$DOWNLOAD_DIR/$PYTHON_INSTALLER"

if [ ! -f "$INSTALLER_PATH" ]; then
    echo -e "${RED}❌ El instalador no se pudo descargar${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Descarga completada${NC}"
echo ""

# Inicializar Wine si es necesario
echo "🍷 Verificando configuración de Wine..."
if [ ! -d "$HOME/.wine" ]; then
    echo "Inicializando Wine (esto puede tomar un momento)..."
    winecfg &
    sleep 3
    killall winecfg 2>/dev/null || true
    echo -e "${GREEN}✅ Wine inicializado${NC}"
fi
echo ""

# Instalar Python
echo -e "${BLUE}📦 Instalando Python ${PYTHON_VERSION} en Wine...${NC}"
echo ""
echo "⚠️  IMPORTANTE: Durante la instalación:"
echo "   1. Marca la casilla 'Add Python ${PYTHON_VERSION} to PATH'"
echo "   2. Elige 'Install Now' o 'Customize installation'"
echo "   3. Si aparece 'Install for all users', puedes marcarlo también"
echo ""
echo "Presiona Enter cuando estés listo para continuar..."
read

wine "$INSTALLER_PATH"

# Esperar un poco para que termine la instalación
echo ""
echo "Esperando a que termine la instalación..."
sleep 5

# Verificar instalación
echo ""
echo "🔍 Verificando instalación..."
if wine python --version &> /dev/null; then
    INSTALLED_VERSION=$(wine python --version 2>&1)
    echo -e "${GREEN}✅ Python instalado correctamente: $INSTALLED_VERSION${NC}"
    echo ""
    
    # Actualizar pip
    echo "📦 Actualizando pip..."
    wine python -m pip install --upgrade pip --quiet 2>/dev/null || {
        echo -e "${YELLOW}⚠️  No se pudo actualizar pip automáticamente${NC}"
        echo "Puedes hacerlo manualmente después con: wine python -m pip install --upgrade pip"
    }
    
    echo ""
    echo -e "${GREEN}🎉 ¡Instalación completada exitosamente!${NC}"
    echo ""
    echo "Ahora puedes ejecutar: ./build_exe_wine.sh"
else
    echo -e "${RED}❌ Python no se instaló correctamente${NC}"
    echo ""
    echo "Posibles soluciones:"
    echo "1. Verifica que marcaste 'Add Python to PATH' durante la instalación"
    echo "2. Intenta instalar manualmente ejecutando: wine $INSTALLER_PATH"
    echo "3. Verifica los logs de Wine para más detalles"
    exit 1
fi


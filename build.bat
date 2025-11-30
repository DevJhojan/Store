@echo off
REM Script para construir ejecutable para Windows

echo 🔨 Construyendo ejecutable para Windows...

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    exit /b 1
)

REM Instalar dependencias si es necesario
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    pip install pyinstaller
)

REM Limpiar builds anteriores
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist main.spec del main.spec

REM Construir ejecutable
echo 📦 Ejecutando PyInstaller...
pyinstaller --clean pyinstaller_windows.spec

echo ✅ Ejecutable creado en: dist\StoreManagement.exe
echo 📁 El archivo .exe está listo para distribuir

pause


#!/bin/bash
set -e

APP_NAME="Max3D Creations Manager"
APP_DIR="/opt/max3d-manager"
DESKTOP_FILE="/usr/share/applications/max3d-manager.desktop"
ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo " Instalando $APP_NAME"
echo "============================================"

if [ "$EUID" -ne 0 ]; then
    echo "Ejecutar con sudo: sudo ./install.sh"
    exit 1
fi

echo ""
echo "[1/5] Verificando dependencias..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no encontrado. Instalar con: sudo apt install python3"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Instalando pip3..."
    apt-get update -qq && apt-get install -y -qq python3-pip
fi

echo "Instalando librerías del sistema..."
apt-get install -y -qq libxcb-cursor0 2>/dev/null || true

echo "[2/5] Instalando dependencias Python..."
pip3 install PySide6 matplotlib reportlab openpyxl --quiet --break-system-packages 2>/dev/null || \
pip3 install PySide6 matplotlib reportlab openpyxl --quiet

echo "[3/5] Copiando archivos..."
mkdir -p "$APP_DIR"
cp -r "$SCRIPT_DIR/app" "$APP_DIR/"
cp "$SCRIPT_DIR/main.py" "$APP_DIR/"
cp -r "$SCRIPT_DIR/resources" "$APP_DIR/"
chmod +x "$APP_DIR/main.py"

echo "[4/5] Instalando icono..."
mkdir -p "$ICON_DIR"
cp "$SCRIPT_DIR/resources/icon.svg" "$ICON_DIR/max3d-manager.svg"
gtk-update-icon-cache -f /usr/share/icons/hicolor/ 2>/dev/null || true

echo "[5/5] Instalando acceso directo..."
cp "$SCRIPT_DIR/max3d-manager.desktop" "$DESKTOP_FILE"
chmod 644 "$DESKTOP_FILE"

echo ""
echo "============================================"
echo " Instalación completada"
echo "============================================"
echo ""
echo "Para ejecutar:"
echo "  python3 /opt/max3d-manager/main.py"
echo ""
echo "O desde el menú de aplicaciones: Max3D Creations Manager"
echo ""

#!/bin/bash
set -e
cd "$(dirname "$0")"
test -x .venv/bin/pyinstaller || ./instalar_macos.command
.venv/bin/pyinstaller --noconfirm --clean --windowed --name "PDV SAT Pro" main.py
echo "Aplicativo criado em dist/PDV SAT Pro.app"
read -r -p "Pressione Enter para concluir."

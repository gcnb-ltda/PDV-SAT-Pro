#!/bin/bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null; then
  echo "Python 3.11+ não encontrado. Instale em https://www.python.org/downloads/macos/"
  read -r -p "Pressione Enter para sair."
  exit 1
fi
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
chmod +x iniciar_macos.command build_macos.command
echo "Instalação concluída. Abra iniciar_macos.command"
read -r -p "Pressione Enter para concluir."

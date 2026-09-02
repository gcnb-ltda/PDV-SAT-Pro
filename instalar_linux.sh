#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "Instale Python 3.11+ e python3-venv."; exit 1; }
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
chmod +x iniciar_linux.sh build_linux.sh
echo "Instalação concluída. Execute ./iniciar_linux.sh"

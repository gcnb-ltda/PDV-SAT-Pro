#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
test -x .venv/bin/pyinstaller || ./instalar_linux.sh
.venv/bin/pyinstaller --noconfirm --clean pdv_sat_pro.spec
echo "Executável criado em dist/PDV-SAT-Pro"

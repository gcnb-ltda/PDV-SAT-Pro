#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
test -x .venv/bin/python || ./instalar_linux.sh
exec .venv/bin/python main.py

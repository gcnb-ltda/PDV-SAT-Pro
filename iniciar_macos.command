#!/bin/bash
set -e
cd "$(dirname "$0")"
test -x .venv/bin/python || ./instalar_macos.command
exec .venv/bin/python main.py

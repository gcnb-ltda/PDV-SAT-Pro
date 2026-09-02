@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe call install_windows.bat
.venv\Scripts\python.exe main.py
if errorlevel 1 pause

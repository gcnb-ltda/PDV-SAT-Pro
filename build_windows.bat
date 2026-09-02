@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe call install_windows.bat
.venv\Scripts\pyinstaller.exe --noconfirm --clean pdv_sat_pro.spec
echo Executavel criado em dist\PDV-SAT-Pro.exe
pause

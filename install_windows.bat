@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul && (set "PY_CMD=py -3") || (set "PY_CMD=python")
%PY_CMD% --version >nul 2>nul || goto :nopython
%PY_CMD% -m venv .venv || goto :error
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt || goto :error
if not exist .env copy .env.example .env >nul
echo.
echo Instalacao concluida. Use iniciar_windows.bat
pause
exit /b 0
:nopython
echo Python 3.11 ou superior nao encontrado.
echo Instale em https://www.python.org/downloads/ marcando Add Python to PATH.
pause
exit /b 1
:error
echo Falha na instalacao. Verifique sua internet e as mensagens acima.
pause
exit /b 1

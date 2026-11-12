@echo off
setlocal
cd /d "%~dp0"
echo =============================================
echo  CampusIA - instalacion (Python recomendado: 3.11+)
echo =============================================
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m venv .venv
) else (
    python -m venv .venv
)
if errorlevel 1 (
    echo ERROR: instala Python desde python.org marcando Add Python to PATH.
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo.
echo INSTALACION COMPLETA. Abre iniciar.bat
pause
exit /b 0
:fail
echo ERROR durante instalacion. Comprueba conexion a internet y Python.
pause
exit /b 1

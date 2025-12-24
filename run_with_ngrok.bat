@echo off
REM Script para ejecutar la aplicación con ngrok en Windows

echo.
echo ========================================
echo INICIANDO APLICACION CON NGROK
echo ========================================
echo.

REM Verificar que ngrok está instalado
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [X] ngrok no está instalado
    echo.
    echo Para instalar ngrok:
    echo 1. Descarga desde: https://ngrok.com/download
    echo 2. O usa: pip install ngrok-cli
    echo 3. Asegúrate de que está en tu PATH
    echo.
    pause
    exit /b 1
)

echo [OK] ngrok está instalado
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

REM Iniciar Flask en background
echo [*] Iniciando servidor Flask en http://127.0.0.1:5000...
start "Flask Server" python run.py

REM Esperar a que Flask se inicie
timeout /t 3 /nobreak

REM Iniciar ngrok
echo [*] Conectando con ngrok...
echo.
echo ========================================
echo APLICACION EN EJECUCION
echo ========================================
echo Local:  http://127.0.0.1:5000
echo Pulsa Ctrl+C para detener
echo ========================================
echo.

ngrok http 5000 --log=stdout

pause

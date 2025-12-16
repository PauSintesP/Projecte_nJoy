@echo off
echo ======================================
echo   SETUP: PROMOTOR DE PRUEBA
echo ======================================

cd /d "%~dp0"

rem Activar el entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

rem Ejecutar el script
python setup_test_stats.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo ejecutar el script
    pause
    exit /b 1
)

echo.
echo ======================================
echo   SETUP COMPLETADO!
echo ======================================
echo.
echo Credenciales de prueba:
echo   Email: promotor@test.com
echo   Password: test123
echo.
pause

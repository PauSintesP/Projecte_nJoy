@echo off
cls
echo ================================================
echo    nJoy Backend - Iniciando en modo LOCAL
echo ================================================
echo.

REM Establecer variables de entorno para SQLite local
set ENV=local
set DATABASE_URL=sqlite:///./njoy_local.db
set DEBUG=True

echo Configuracion:
echo - ENV: %ENV%
echo - DATABASE: SQLite local (njoy_local.db)
echo - DEBUG: %DEBUG%
echo.
echo Iniciando servidor en http://localhost:8000
echo Documentacion en http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo ================================================
echo.

py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

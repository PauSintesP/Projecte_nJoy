@echo off
REM Script para iniciar el backend con la configuración correcta de desarrollo local
echo Iniciando backend en modo desarrollo local...

REM Configurar la variable de entorno DATABASE_URL solo para esta sesión
set DATABASE_URL=sqlite:///./njoy_local.db
set ENV=local
set DEBUG=True

REM Iniciar el servidor uvicorn
C:\Users\pausi\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

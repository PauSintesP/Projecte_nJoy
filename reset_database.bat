@echo off
echo =========================================
echo   RESETEAR BASE DE DATOS - nJoy
echo =========================================
echo.
echo ADVERTENCIA: Esto eliminara TODOS los datos!
echo Solo se conservara el usuario admin.
echo.
pause

echo.
echo Paso 1: Eliminando todas las tablas...
curl http://localhost:8000/drop-and-recreate-db
echo.
echo.

echo Paso 2: Creando tablas y usuario admin...
curl http://localhost:8000/init-db
echo.
echo.

echo =========================================
echo   Base de datos reseteada exitosamente!
echo =========================================
echo.
echo Usuario admin creado:
echo   Email: admin@njoy.com
echo   Password: admin123
echo.
pause

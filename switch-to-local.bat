@echo off
REM ========================================
REM   SWITCH TO LOCAL DEVELOPMENT
REM   Changes: Web Frontend + Mobile App
REM ========================================
echo.
echo ========================================
echo   SWITCHING TO LOCAL ENVIRONMENT
echo ========================================
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP: =%

echo Detected Local IP: %LOCAL_IP%
echo.

REM ==========================================
REM 1. Change Web Frontend (.env)
REM ==========================================
echo [1/2] Updating Web Frontend...
cd /d "%~dp0\..\web-njoy"
echo VITE_API_URL=http://localhost:8000> .env
echo      ✅ Frontend now points to: http://localhost:8000
echo.

REM ==========================================
REM 2. Change Mobile App (ApiService.kt)
REM ==========================================
echo [2/2] Updating Mobile App...
cd /d "%~dp0\..\njoy"
set FILE=app\src\main\java\com\example\njoy\ApiService.kt

REM Create backup
copy "%FILE%" "%FILE%.backup" >nul 2>&1

REM Replace URLs using PowerShell
powershell -Command "(Get-Content '%FILE%') -replace 'private const val BASE_URL = \"https://projecte-n-joy.vercel.app/\"', '// private const val BASE_URL = \"https://projecte-n-joy.vercel.app/\"' | Set-Content '%FILE%'"
powershell -Command "(Get-Content '%FILE%') -replace '// private const val BASE_URL = \"http://.*:8000/\"', 'private const val BASE_URL = \"http://%LOCAL_IP%:8000/\"' | Set-Content '%FILE%'"

echo      ✅ Mobile App now points to: http://%LOCAL_IP%:8000/
echo.

REM ==========================================
REM Summary
REM ==========================================
echo ========================================
echo   ✅ SWITCHED TO LOCAL ENVIRONMENT
echo ========================================
echo.
echo NEXT STEPS:
echo   Web:    Restart dev server (Ctrl+C then 'npm run dev')
echo   Mobile: Rebuild app in Android Studio
echo.
pause

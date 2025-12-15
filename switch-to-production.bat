@echo off
REM ========================================
REM   SWITCH TO PRODUCTION
REM   Changes: Web Frontend + Mobile App
REM ========================================
echo.
echo ========================================
echo   SWITCHING TO PRODUCTION ENVIRONMENT
echo ========================================
echo.

REM ==========================================
REM 1. Change Web Frontend (.env)
REM ==========================================
echo [1/2] Updating Web Frontend...
cd /d "%~dp0\..\web-njoy"
echo VITE_API_URL=https://projecte-n-joy.vercel.app> .env
echo      ✅ Frontend now points to: https://projecte-n-joy.vercel.app
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
powershell -Command "(Get-Content '%FILE%') -replace '// private const val BASE_URL = \"https://projecte-n-joy.vercel.app/\"', 'private const val BASE_URL = \"https://projecte-n-joy.vercel.app/\"' | Set-Content '%FILE%'"
powershell -Command "(Get-Content '%FILE%') -replace 'private const val BASE_URL = \"http://.*:8000/\"', '// private const val BASE_URL = \"http://192.168.1.132:8000/\"' | Set-Content '%FILE%'"

echo      ✅ Mobile App now points to: https://projecte-n-joy.vercel.app/
echo.

REM ==========================================
REM Summary
REM ==========================================
echo ========================================
echo   ✅ SWITCHED TO PRODUCTION ENVIRONMENT
echo ========================================
echo.
echo NEXT STEPS:
echo   Web:    Restart dev server (Ctrl+C then 'npm run dev')
echo   Mobile: Rebuild app in Android Studio
echo.
pause

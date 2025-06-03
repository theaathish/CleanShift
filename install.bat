@echo off
echo 🚀 Installing CleanShift...

REM Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Administrator privileges required
    echo Please right-click and "Run as administrator"
    pause
    exit /b 1
)

echo 📥 Downloading CleanShift...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe' -OutFile '%TEMP%\cleanshift.exe' -UseBasicParsing"

if not exist "%TEMP%\cleanshift.exe" (
    echo ❌ Download failed
    pause
    exit /b 1
)

echo ⚙️  Installing to system...
"%TEMP%\cleanshift.exe" install

echo.
echo ✅ CleanShift installed successfully!
echo 💡 Usage examples:
echo    cleanshift status
echo    cleanshift analyze
echo    cleanshift clean --temp-files
pause

@echo off
echo 🚀 Installing CleanShift GUI...

echo 📥 Downloading CleanShift...
powershell -Command "iwr -useb https://github.com/theaathish/CleanShift/raw/main/install.ps1 | iex"

echo.
echo ✅ Installation complete!
echo Double-click the CleanShift shortcut on your desktop to launch.
pause

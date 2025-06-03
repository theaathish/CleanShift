import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build command
    build_cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name", "cleanshift",
        "--icon", "assets/icon.ico" if os.path.exists("assets/icon.ico") else None,
        "--add-data", "cleanshift;cleanshift",
        "--hidden-import", "click",
        "--hidden-import", "rich",
        "--hidden-import", "psutil",
        "--hidden-import", "win32api",
        "--hidden-import", "win32file",
        "cleanshift/main.py"
    ]
    
    # Remove None values
    build_cmd = [cmd for cmd in build_cmd if cmd is not None]
    
    print("Building standalone executable...")
    try:
        subprocess.check_call(build_cmd)
        print("\n✅ Build successful!")
        print("📦 Executable created at: dist/cleanshift.exe")
        print("\n📋 To distribute:")
        print("1. Share the dist/cleanshift.exe file")
        print("2. Users can run: cleanshift.exe install")
        print("3. Then use: cleanshift <command>")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()

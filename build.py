import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build standalone GUI executable using PyInstaller"""
    
    # Install PyInstaller with specific version for compatibility
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller==5.13.2"])
    
    # Install Pillow for image support
    try:
        import PIL
    except ImportError:
        print("Installing Pillow for image support...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    
    # Create assets directory if it doesn't exist
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Build command for GUI-only executable
    build_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",  # No console window
        "--name", "cleanshift",
        "--icon", "assets/icon.ico" if os.path.exists("assets/icon.ico") else None,
        "--add-data", "cleanshift;cleanshift",
        "--add-data", "assets;assets",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.messagebox", 
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageTk",
        "--hidden-import", "psutil",
        "--hidden-import", "win32api",
        "--hidden-import", "win32file",
        "--hidden-import", "win32con",
        "--exclude-module", "click",
        "--exclude-module", "rich",
        "cleanshift/main.py"
    ]
    
    # Remove None values
    build_cmd = [cmd for cmd in build_cmd if cmd is not None]
    
    print("Building standalone GUI executable...")
    try:
        subprocess.check_call(build_cmd)
        print("\n✅ Build successful!")
        print("📦 GUI Executable created at: dist/cleanshift.exe")
        print("\n📋 To distribute:")
        print("1. Share the dist/cleanshift.exe file")
        print("2. Users can double-click to run")
        print("3. No installation required - standalone GUI")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_executable()

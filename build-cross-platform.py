#!/usr/bin/env python3
"""
Cross-platform build script for CleanShift
Works from macOS to build Windows executables using GitHub Actions
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def install_dependencies():
    """Install required build dependencies"""
    dependencies = [
        "pyinstaller",
        "click",
        "rich", 
        "psutil",
        "colorama"
    ]
    
    print("Installing dependencies...")
    for dep in dependencies:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

def create_windows_spec():
    """Create PyInstaller spec file optimized for Windows"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cleanshift/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('cleanshift/*.py', 'cleanshift'),
    ],
    hiddenimports=[
        'click',
        'rich.console',
        'rich.table',
        'rich.progress',
        'rich.text',
        'psutil',
        'colorama',
        'platform',
        'shutil',
        'subprocess',
        'pathlib',
        'tempfile',
        'json',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'win32api',
        'win32file',
        'win32com',
        'winreg',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='cleanshift',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('cleanshift-cross.spec', 'w') as f:
        f.write(spec_content.strip())

def build_cross_platform():
    """Build executable that works on current platform"""
    print(f"Building executable for {platform.system()}...")
    
    # Create spec file
    create_windows_spec()
    
    # Determine output name based on platform
    if platform.system() == "Windows":
        exe_name = "cleanshift.exe"
    else:
        exe_name = "cleanshift"
    
    # Build command
    build_cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--console",
        "--name", "cleanshift",
        "--add-data", "cleanshift:cleanshift",
        "--hidden-import", "click",
        "--hidden-import", "rich",
        "--hidden-import", "psutil",
        "--hidden-import", "colorama",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib", 
        "--exclude-module", "numpy",
        "cleanshift/main.py"
    ]
    
    try:
        subprocess.check_call(build_cmd)
        
        exe_path = Path(f"dist/{exe_name}")
        if exe_path.exists():
            print(f"✅ Executable built successfully!")
            print(f"📁 Location: {exe_path.absolute()}")
            print(f"📦 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print("❌ Build failed - executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_github_workflow():
    """Create GitHub Actions workflow for Windows builds"""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: Build Windows Executable

on:
  push:
    branches: [ main, master ]
    tags: [ 'v*' ]
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller click rich psutil colorama pywin32
    
    - name: Build Windows executable
      run: |
        pyinstaller --onefile --console --name cleanshift --add-data "cleanshift;cleanshift" --hidden-import click --hidden-import rich --hidden-import psutil --hidden-import colorama --hidden-import win32api --hidden-import win32file --hidden-import winreg cleanshift/main.py
    
    - name: Test executable
      run: |
        dist\\cleanshift.exe --version
    
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: cleanshift-windows-exe
        path: dist/cleanshift.exe
        retention-days: 30
    
    - name: Create Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/cleanshift.exe
        body: |
          ## CleanShift Windows Release ${{ github.ref_name }}
          
          ### 🚀 Quick Install
          ```cmd
          curl -L https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe -o cleanshift.exe
          cleanshift.exe install
          ```
          
          ### 📋 Manual Install
          1. Download `cleanshift.exe`
          2. Run as administrator: `cleanshift.exe install`
          3. Use globally: `cleanshift <command>`
          
          ### ⚡ Features
          - Standalone executable (no dependencies)
          - System PATH integration
          - Drive space analysis and cleanup
          - Safe file operations with dry-run mode
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''
    
    with open(workflow_dir / "build.yml", "w") as f:
        f.write(workflow_content)
    
    print("📄 Created GitHub Actions workflow")

def create_installer_scripts():
    """Create installation scripts for end users"""
    
    # PowerShell installer
    ps_installer = '''# CleanShift One-Command Installer
Write-Host "🚀 Installing CleanShift..." -ForegroundColor Green

# Check admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "⚠️  Administrator privileges required" -ForegroundColor Yellow
    Write-Host "Please run PowerShell as administrator" -ForegroundColor Red
    exit 1
}

try {
    $url = "https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe"
    $temp = "$env:TEMP\\cleanshift.exe"
    
    Write-Host "📥 Downloading CleanShift..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $url -OutFile $temp -UseBasicParsing
    
    Write-Host "⚙️  Installing to system..." -ForegroundColor Cyan
    & $temp install
    
    Write-Host ""
    Write-Host "✅ CleanShift installed successfully!" -ForegroundColor Green
    Write-Host "💡 Usage examples:" -ForegroundColor White
    Write-Host "   cleanshift status" -ForegroundColor Gray
    Write-Host "   cleanshift analyze" -ForegroundColor Gray
    Write-Host "   cleanshift clean --temp-files" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check your internet connection" -ForegroundColor Yellow
}
'''
    
    with open("install.ps1", "w") as f:
        f.write(ps_installer)
    
    # Batch installer
    batch_installer = '''@echo off
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
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe' -OutFile '%TEMP%\\cleanshift.exe' -UseBasicParsing"

if not exist "%TEMP%\\cleanshift.exe" (
    echo ❌ Download failed
    pause
    exit /b 1
)

echo ⚙️  Installing to system...
"%TEMP%\\cleanshift.exe" install

echo.
echo ✅ CleanShift installed successfully!
echo 💡 Usage examples:
echo    cleanshift status
echo    cleanshift analyze
echo    cleanshift clean --temp-files
pause
'''
    
    with open("install.bat", "w") as f:
        f.write(batch_installer)
    
    print("📄 Created install.ps1 and install.bat")

def main():
    """Main build process"""
    print("🔨 CleanShift Cross-Platform Builder")
    print(f"🖥️  Building from: {platform.system()}")
    
    if platform.system() != "Windows":
        print("⚠️  Building from non-Windows platform")
        print("📝 Creating GitHub Actions workflow for Windows builds...")
        create_github_workflow()
        create_installer_scripts()
        
        print("\n🎯 Next steps:")
        print("1. Commit and push: git add . && git commit -m 'Setup build system' && git push")
        print("2. Create release: git tag v1.0.0 && git push origin v1.0.0")
        print("3. GitHub Actions will build Windows executable automatically")
        print("4. Users install with: https://github.com/theaathish/CleanShift/releases/latest")
        return
    
    # Install dependencies
    install_dependencies()
    
    # Build executable
    if build_cross_platform():
        create_installer_scripts()
        
        print("\n🎉 Build complete!")
        print("📋 Test the executable:")
        print("   dist/cleanshift.exe --help")
        print("📤 Ready for distribution!")
    else:
        print("\n❌ Build failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

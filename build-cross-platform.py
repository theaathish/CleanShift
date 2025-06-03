#!/usr/bin/env python3
"""
Cross-platform build script for CleanShift GUI
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
        "psutil",
        "pillow"
    ]
    
    if platform.system() == "Windows":
        dependencies.append("pywin32")
    
    print("Installing dependencies...")
    for dep in dependencies:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

def create_github_workflow():
    """Create GitHub Actions workflow for GUI builds"""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = '''name: Build Windows GUI Executable

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
        pip install pyinstaller tkinter psutil pillow pywin32
    
    - name: Create assets directory
      run: |
        mkdir -p assets
        echo "# Placeholder for assets" > assets/README.md
    
    - name: Build Windows GUI executable
      run: |
        pyinstaller --onefile --windowed --name cleanshift --add-data "cleanshift;cleanshift" --add-data "assets;assets" --hidden-import tkinter --hidden-import PIL --hidden-import psutil --hidden-import win32api --hidden-import win32file cleanshift/main.py
    
    - name: Test executable exists
      run: |
        if (Test-Path "dist\\cleanshift.exe") { 
          Write-Host "✅ Build successful" 
          $size = (Get-Item "dist\\cleanshift.exe").Length / 1MB
          Write-Host "📦 Executable size: $([math]::Round($size, 2)) MB"
        } else { 
          Write-Host "❌ Build failed"
          exit 1 
        }
    
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: cleanshift-windows-gui
        path: dist/cleanshift.exe
        retention-days: 30
    
    - name: Create Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/cleanshift.exe
        body: |
          ## CleanShift GUI Release ${{ github.ref_name }}
          
          ### 🚀 Quick Install
          ```powershell
          iwr -useb https://github.com/theaathish/CleanShift/raw/main/install.ps1 | iex
          ```
          
          ### 📋 Manual Install
          1. Download `cleanshift.exe`
          2. Double-click to run
          3. No installation required!
          
          ### ✨ Features
          - Modern GUI interface
          - System cleanup and optimization
          - Drive space analysis
          - Application management
          - Development environment cleanup
          - Standalone executable
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''
    
    with open(workflow_dir / "build.yml", "w") as f:
        f.write(workflow_content)
    
    print("📄 Created GitHub Actions workflow")

def create_installer_scripts():
    """Create installation scripts for end users"""
    
    # PowerShell installer for GUI
    ps_installer = '''# CleanShift GUI Installer
Write-Host "🚀 Installing CleanShift GUI..." -ForegroundColor Green

try {
    $url = "https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe"
    $installDir = "$env:LOCALAPPDATA\\CleanShift"
    $exePath = "$installDir\\cleanshift.exe"
    
    Write-Host "📥 Downloading CleanShift..." -ForegroundColor Cyan
    
    # Create install directory
    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }
    
    # Download executable
    Invoke-WebRequest -Uri $url -OutFile $exePath -UseBasicParsing
    
    # Create desktop shortcut
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\CleanShift.lnk")
    $Shortcut.TargetPath = $exePath
    $Shortcut.WorkingDirectory = $installDir
    $Shortcut.Description = "CleanShift - System Cleanup & Optimizer"
    $Shortcut.Save()
    
    Write-Host ""
    Write-Host "✅ CleanShift installed successfully!" -ForegroundColor Green
    Write-Host "🖥️  Double-click desktop shortcut to launch" -ForegroundColor White
    
} catch {
    Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
}
'''
    
    with open("install.ps1", "w") as f:
        f.write(ps_installer)
    
    # Batch installer
    batch_installer = '''@echo off
echo 🚀 Installing CleanShift GUI...

echo 📥 Downloading CleanShift...
powershell -Command "iwr -useb https://github.com/theaathish/CleanShift/raw/main/install.ps1 | iex"

echo.
echo ✅ Installation complete!
echo Double-click the CleanShift shortcut on your desktop to launch.
pause
'''
    
    with open("install.bat", "w") as f:
        f.write(batch_installer)
    
    print("📄 Created install.ps1 and install.bat")

def main():
    """Main build process"""
    print("🔨 CleanShift GUI Builder")
    print(f"🖥️  Building from: {platform.system()}")
    
    if platform.system() != "Windows":
        print("⚠️  Building from non-Windows platform")
        print("📝 Creating GitHub Actions workflow for Windows GUI builds...")
        create_github_workflow()
        create_installer_scripts()
        
        print("\n🎯 Next steps:")
        print("1. Commit and push: git add . && git commit -m 'Setup GUI build system' && git push")
        print("2. Create release: git tag v1.0.0 && git push origin v1.0.0")
        print("3. GitHub Actions will build Windows GUI executable automatically")
        print("4. Users install with: iwr -useb <your-repo>/install.ps1 | iex")
        return
    
    # For Windows, try local build
    install_dependencies()
    
    try:
        build_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name", "cleanshift",
            "--add-data", "cleanshift;cleanshift",
            "--hidden-import", "tkinter",
            "--hidden-import", "PIL",
            "--hidden-import", "psutil",
            "cleanshift/main.py"
        ]
        
        subprocess.check_call(build_cmd)
        print("\n🎉 GUI Build complete!")
        print("📦 Executable: dist/cleanshift.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Local build failed: {e}")
        print("Use GitHub Actions for reliable builds")

if __name__ == "__main__":
    main()

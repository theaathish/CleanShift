# CleanShift GUI Installer
Write-Host "🚀 Installing CleanShift GUI..." -ForegroundColor Green

try {
    $url = "https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe"
    $installDir = "$env:LOCALAPPDATA\CleanShift"
    $exePath = "$installDir\cleanshift.exe"
    
    Write-Host "📥 Downloading CleanShift..." -ForegroundColor Cyan
    
    # Create install directory
    if (-not (Test-Path $installDir)) {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    }
    
    # Download executable
    Invoke-WebRequest -Uri $url -OutFile $exePath -UseBasicParsing
    
    # Create desktop shortcut
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\CleanShift.lnk")
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

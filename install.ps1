# CleanShift One-Command Installer
Write-Host "🚀 Installing CleanShift..." -ForegroundColor Green

# Check admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "⚠️  Administrator privileges required" -ForegroundColor Yellow
    Write-Host "Please run PowerShell as administrator" -ForegroundColor Red
    exit 1
}

try {
    $url = "https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe"
    $temp = "$env:TEMP\cleanshift.exe"
    
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

# CleanShift PowerShell Installer

Write-Host "Installing CleanShift..." -ForegroundColor Green

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires administrator privileges." -ForegroundColor Red
    Write-Host "Please run PowerShell as administrator and try again." -ForegroundColor Yellow
    exit 1
}

try {
    # Download CleanShift executable
    Write-Host "Downloading CleanShift..." -ForegroundColor Yellow
    $downloadUrl = "https://github.com/theaathish/CleanShift/releases/latest/download/cleanshift.exe"
    $tempPath = "$env:TEMP\cleanshift.exe"
    
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempPath -UseBasicParsing
    
    if (!(Test-Path $tempPath)) {
        throw "Download failed"
    }
    
    # Install CleanShift
    Write-Host "Installing CleanShift to system..." -ForegroundColor Yellow
    & $tempPath install
    
    Write-Host ""
    Write-Host "Installation complete!" -ForegroundColor Green
    Write-Host "You can now use 'cleanshift' command from any command prompt." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Example commands:" -ForegroundColor White
    Write-Host "  cleanshift status" -ForegroundColor Gray
    Write-Host "  cleanshift analyze" -ForegroundColor Gray
    Write-Host "  cleanshift clean --temp-files --browser-cache" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again." -ForegroundColor Yellow
    exit 1
}

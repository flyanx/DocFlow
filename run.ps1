# DocFlow Launcher (PowerShell)
Set-Location $PSScriptRoot
Write-Host "=========================================="
Write-Host "   DocFlow"
Write-Host "=========================================="
Write-Host ""
Write-Host "Starting, please wait..."
Write-Host ""

$python = "F:\doc_converter_env\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "[ERROR] Python not found at $python" -ForegroundColor Red
    Write-Host "Please run install.bat first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

& $python app.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Failed to start." -ForegroundColor Red
    Write-Host "Check error messages above." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}

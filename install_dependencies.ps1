# PowerShell script to install dependencies for IDU XML Generator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing IDU XML Generator Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Try to find Python 3.11
$pythonCommands = @(
    "python3.11",
    "python3",
    "python",
    "py -3.11"
)

$found = $false

foreach ($cmd in $pythonCommands) {
    Write-Host "Trying: $cmd" -ForegroundColor Yellow
    
    try {
        $result = & $cmd -m pip install openpyxl xlrd 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Successfully installed dependencies using $cmd!" -ForegroundColor Green
            $found = $true
            break
        }
    } catch {
        # Continue to next command
    }
}

if (-not $found) {
    Write-Host ""
    Write-Host "ERROR: Could not find Python installation." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install dependencies manually:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: If Python 3.11 is installed, find it and run:" -ForegroundColor Cyan
    Write-Host "   [Python3.11Path]\python.exe -m pip install openpyxl xlrd" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Or install all requirements:" -ForegroundColor Cyan
    Write-Host "   [Python3.11Path]\python.exe -m pip install -r requirements_idu_xml.txt" -ForegroundColor White
    Write-Host ""
    Write-Host "Common Python 3.11 installation paths:" -ForegroundColor Yellow
    Write-Host "   C:\Python311\python.exe" -ForegroundColor White
    Write-Host "   C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe" -ForegroundColor White
    Write-Host "   C:\Program Files\Python311\python.exe" -ForegroundColor White
    Write-Host ""
}

Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


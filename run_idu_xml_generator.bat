@echo off
echo Starting IDU XML Generator App...
echo.

REM Check if dependencies are installed
python -c "import openpyxl, xlrd" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Required dependencies (openpyxl, xlrd) may not be installed.
    echo.
    echo Please run install_dependencies.bat first, or install manually:
    echo    pip install openpyxl xlrd
    echo.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
)

streamlit run idu_xml_generator_app.py
pause


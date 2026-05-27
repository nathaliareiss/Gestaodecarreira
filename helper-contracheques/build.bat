@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not exist ".venv" (
  python -m venv .venv
)

call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
powershell.exe -ExecutionPolicy Bypass -File "scripts\generate-installer-icon.ps1"
python -m PyInstaller --clean --noconfirm helper.spec

if not exist "..\backend\static\downloads" mkdir "..\backend\static\downloads"

where iscc >nul 2>nul
if %errorlevel%==0 (
  iscc installer\GestaoDeCarreira-Setup.iss
) else (
  echo Inno Setup nao encontrado. O instalador real nao foi gerado.
)

echo.
echo Build concluido. O executavel deve ficar em dist\GestaoDeCarreira-Assistente.exe
echo O instalador real deve ficar em backend\static\downloads\GestaoDeCarreira-Setup-1.0.4.exe
endlocal

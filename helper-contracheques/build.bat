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
python -m PyInstaller --clean --noconfirm helper.spec

if not exist "..\backend\static\downloads" mkdir "..\backend\static\downloads"
copy /Y "dist\GestaoDeCarreira-Assistente.exe" "..\backend\static\downloads\gestao-de-carreira-assistente.exe"

echo.
echo Build concluido. O executavel deve ficar em dist\GestaoDeCarreira-Assistente.exe
endlocal

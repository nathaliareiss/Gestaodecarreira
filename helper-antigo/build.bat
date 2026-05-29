@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "APP_VERSION=1.0.9"

if exist "..\build" rmdir /S /Q "..\build"
if exist "..\dist" rmdir /S /Q "..\dist"
if exist "dist\GestaoDeCarreira-Assistente" rmdir /S /Q "dist\GestaoDeCarreira-Assistente"
if exist "dist\installer" rmdir /S /Q "dist\installer"

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
  if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\GestaoDeCarreira-Setup.iss
  ) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" installer\GestaoDeCarreira-Setup.iss
  ) else (
    echo Inno Setup nao encontrado. O instalador real nao foi gerado.
  )
)

echo.
echo Build concluido. O executavel deve ficar em dist\GestaoDeCarreira-Assistente\GestaoDeCarreira-Assistente.exe
if exist "dist\installer\GestaoDeCarreira-Setup-%APP_VERSION%.exe" (
  copy /Y "dist\installer\GestaoDeCarreira-Setup-%APP_VERSION%.exe" "..\backend\static\downloads\GestaoDeCarreira-Setup-%APP_VERSION%.exe" >nul
  copy /Y "dist\installer\GestaoDeCarreira-Setup-%APP_VERSION%.exe" "..\backend\static\downloads\GestaoDeCarreira-Setup-latest.exe" >nul
)
echo O instalador real deve ficar em backend\static\downloads\GestaoDeCarreira-Setup-%APP_VERSION%.exe
echo O alias atual fica em backend\static\downloads\GestaoDeCarreira-Setup-latest.exe
endlocal

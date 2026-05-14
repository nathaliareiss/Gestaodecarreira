Param(
    [switch]$OneFile,
    [switch]$Installer
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium

$iconArg = @()
if (Test-Path "assets\helper-contracheques.ico") {
    $iconArg = @("--icon", "assets\helper-contracheques.ico")
}

if ($OneFile) {
    $versionArg = @()
    if (Test-Path "version_info.txt") {
        $versionArg = @("--version-file", "version_info.txt")
    }
    .\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm --onefile --name GestaoDeCarreira-Assistente @versionArg @iconArg main.py
} else {
    .\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm helper.spec
}

if ($Installer) {
    powershell.exe -ExecutionPolicy Bypass -File "scripts\generate-installer-icon.ps1"
    $iscc = Get-Command iscc -ErrorAction SilentlyContinue
    if (-not $iscc) {
        throw "Inno Setup nao encontrado no PATH."
    }

    & $iscc.Source "installer\GestaoDeCarreira-Setup.iss"
}

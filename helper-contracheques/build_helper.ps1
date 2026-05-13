Param(
    [switch]$OneFile
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
    .\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm --onefile --name helper-contracheques @iconArg main.py
} else {
    .\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm helper-contracheques.spec
}

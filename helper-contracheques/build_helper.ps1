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
    .\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm --onefile --name GestaoDeCarreira-Assistente @versionArg @iconArg bootstrap.py
} else {
    .\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm helper.spec
}

if ($Installer) {
    powershell.exe -ExecutionPolicy Bypass -File "scripts\generate-installer-icon.ps1"
    $iscc = Get-Command iscc -ErrorAction SilentlyContinue
    if (-not $iscc) {
        $candidatePaths = @(
            "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            "C:\Program Files\Inno Setup 6\ISCC.exe"
        )
        foreach ($candidate in $candidatePaths) {
            if (Test-Path $candidate) {
                $iscc = [pscustomobject]@{ Source = $candidate }
                break
            }
        }
    }

    if (-not $iscc) {
        throw "Inno Setup nao encontrado no PATH nem nos locais padrao."
    }

    & $iscc.Source "installer\GestaoDeCarreira-Setup.iss"

    $downloadsRoot = "..\backend\static\downloads"
    if (-not (Test-Path $downloadsRoot)) {
        New-Item -ItemType Directory -Force -Path $downloadsRoot | Out-Null
    }

    $downloadsDir = (Resolve-Path $downloadsRoot).Path
    $versionedInstaller = Join-Path $downloadsDir "GestaoDeCarreira-Setup-1.0.5.exe"
    $latestInstaller = Join-Path $downloadsDir "GestaoDeCarreira-Setup-latest.exe"
    if (Test-Path $versionedInstaller) {
        Copy-Item -Force $versionedInstaller $latestInstaller
    }
}

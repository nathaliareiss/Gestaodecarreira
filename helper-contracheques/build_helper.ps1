Param(
    [switch]$OneFile,
    [switch]$Installer,
    [switch]$InstallBrowsers
)

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
$repoRoot = Split-Path $scriptDir -Parent
$appVersion = "1.0.9"

Set-Location $scriptDir

$pathsToClean = @(
    (Join-Path $repoRoot "build"),
    (Join-Path $repoRoot "dist"),
    (Join-Path $scriptDir "build"),
    (Join-Path $scriptDir "dist\GestaoDeCarreira-Assistente"),
    (Join-Path $scriptDir "dist\installer")
)

foreach ($path in $pathsToClean) {
    if (Test-Path $path) {
        try {
            Remove-Item -LiteralPath $path -Recurse -Force
        } catch {
            Write-Warning "Nao foi possivel limpar '$path': $($_.Exception.Message)"
        }
    }
}

if (-not (Test-Path (Join-Path $scriptDir ".venv"))) {
    python -m venv (Join-Path $scriptDir ".venv")
}

& (Join-Path $scriptDir ".venv\Scripts\python.exe") -m pip install --upgrade pip
& (Join-Path $scriptDir ".venv\Scripts\python.exe") -m pip install -r (Join-Path $scriptDir "requirements.txt")

if ($InstallBrowsers) {
    Write-Host "Instalando navegadores do Playwright..."
    & (Join-Path $scriptDir ".venv\Scripts\python.exe") -m playwright install chromium
} else {
    Write-Host "Pulando instalacao do Chromium do Playwright; o helper usa Edge como padrao."
}

$iconArg = @()
if (Test-Path "assets\helper-contracheques.ico") {
    $iconArg = @("--icon", "assets\helper-contracheques.ico")
}

if ($OneFile) {
    $versionArg = @()
    $versionInfoPath = Join-Path $scriptDir "version_info.txt"
    if (Test-Path $versionInfoPath) {
        $versionArg = @("--version-file", $versionInfoPath)
    }
    & (Join-Path $scriptDir ".venv\Scripts\python.exe") -m PyInstaller --clean --noconfirm --onefile --name GestaoDeCarreira-Assistente @versionArg @iconArg (Join-Path $scriptDir "bootstrap.py")
} else {
    & (Join-Path $scriptDir ".venv\Scripts\python.exe") -m PyInstaller --clean --noconfirm (Join-Path $scriptDir "helper.spec")
}

if ($Installer) {
    powershell.exe -ExecutionPolicy Bypass -File (Join-Path $scriptDir "scripts\generate-installer-icon.ps1")
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

    & $iscc.Source (Join-Path $scriptDir "installer\GestaoDeCarreira-Setup.iss")

    $installerBuildRoot = Join-Path $scriptDir "dist\installer"
    $downloadsRoot = Join-Path $repoRoot "backend\static\downloads"

    if (-not (Test-Path $downloadsRoot)) {
        New-Item -ItemType Directory -Force -Path $downloadsRoot | Out-Null
    }

    $installerDir = (Resolve-Path $installerBuildRoot).Path
    $downloadsDir = (Resolve-Path $downloadsRoot).Path
    $versionedInstaller = Join-Path $installerDir "GestaoDeCarreira-Setup-$appVersion.exe"
    $publishedInstaller = Join-Path $downloadsDir "GestaoDeCarreira-Setup-$appVersion.exe"
    $latestInstaller = Join-Path $downloadsDir "GestaoDeCarreira-Setup-latest.exe"
    if (Test-Path $versionedInstaller) {
        Copy-Item -Force $versionedInstaller $publishedInstaller
        Copy-Item -Force $versionedInstaller $latestInstaller
    }
}

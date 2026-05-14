param(
    [string]$OutputPath = (Join-Path $PSScriptRoot "..\assets\installer-icon.ico")
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

function New-RoundedRectanglePath {
    param(
        [System.Drawing.Rectangle]$Bounds,
        [int]$Radius
    )

    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $diameter = $Radius * 2

    $path.AddArc($Bounds.X, $Bounds.Y, $diameter, $diameter, 180, 90)
    $path.AddArc($Bounds.Right - $diameter, $Bounds.Y, $diameter, $diameter, 270, 90)
    $path.AddArc($Bounds.Right - $diameter, $Bounds.Bottom - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($Bounds.X, $Bounds.Bottom - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()

    return $path
}

$outputDir = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$size = 256
$bitmap = New-Object System.Drawing.Bitmap $size, $size
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias

$backgroundRect = New-Object System.Drawing.Rectangle 0, 0, $size, $size
$background = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $backgroundRect,
    [System.Drawing.Color]::FromArgb(255, 16, 185, 129),
    [System.Drawing.Color]::FromArgb(255, 15, 118, 110),
    45
)
$graphics.FillRectangle($background, $backgroundRect)

$haloPath = New-RoundedRectanglePath -Bounds (New-Object System.Drawing.Rectangle 34, 34, 188, 188) -Radius 28
$halo = New-Object System.Drawing.Drawing2D.PathGradientBrush($haloPath)
$halo.CenterColor = [System.Drawing.Color]::FromArgb(80, 255, 255, 255)
$halo.SurroundColors = @([System.Drawing.Color]::FromArgb(0, 255, 255, 255))
$graphics.FillPath($halo, $haloPath)

$shadowRect = New-Object System.Drawing.Rectangle 60, 52, 148, 168
$shadowPath = New-RoundedRectanglePath -Bounds $shadowRect -Radius 22
$shadowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(36, 0, 0, 0))
$graphics.TranslateTransform(0, 6)
$graphics.FillPath($shadowBrush, $shadowPath)
$graphics.ResetTransform()

$cardRect = New-Object System.Drawing.Rectangle 54, 42, 148, 168
$cardPath = New-RoundedRectanglePath -Bounds $cardRect -Radius 22
$cardBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(250, 252, 255))
$graphics.FillPath($cardBrush, $cardPath)

$headerBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 16, 185, 129))
$graphics.FillRectangle($headerBrush, 54, 42, 148, 38)

$panelBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 236, 253, 245))
$graphics.FillRectangle($panelBrush, 68, 100, 120, 16)
$graphics.FillRectangle($panelBrush, 68, 126, 92, 16)
$graphics.FillRectangle($panelBrush, 68, 152, 104, 16)

$linePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 15, 118, 110), 10)
$linePen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$linePen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$graphics.DrawLine($linePen, 82, 180, 104, 196)
$graphics.DrawLine($linePen, 104, 196, 156, 144)

$accentPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(255, 255, 255, 255), 6)
$accentPen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$accentPen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$graphics.DrawLine($accentPen, 84, 78, 138, 78)
$graphics.DrawLine($accentPen, 84, 88, 112, 88)

$handle = [System.IntPtr]::Zero
$icon = $null
$stream = $null

try {
    $handle = $bitmap.GetHicon()
    $icon = [System.Drawing.Icon]::FromHandle($handle)
    $stream = [System.IO.File]::Open($OutputPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write)
    $icon.Save($stream)
} finally {
    if ($stream) { $stream.Dispose() }
    if ($icon) { $icon.Dispose() }
    if ($handle -ne [System.IntPtr]::Zero) {
        Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class NativeMethods {
    [DllImport("user32.dll", SetLastError=true)]
    public static extern bool DestroyIcon(IntPtr hIcon);
}
"@
        [NativeMethods]::DestroyIcon($handle) | Out-Null
    }
    $graphics.Dispose()
    $bitmap.Dispose()
    $background.Dispose()
    $halo.Dispose()
    $shadowBrush.Dispose()
    $cardBrush.Dispose()
    $headerBrush.Dispose()
    $panelBrush.Dispose()
    $linePen.Dispose()
    $accentPen.Dispose()
    $cardPath.Dispose()
    $shadowPath.Dispose()
    $haloPath.Dispose()
}

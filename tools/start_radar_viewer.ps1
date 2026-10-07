param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$viewerRoot = Split-Path $PSScriptRoot -Parent
$viewerUrl = 'http://127.0.0.1:8765'
$viewerRunning = $false
try {
    $viewerState = Invoke-RestMethod "$viewerUrl/api/state?since=0" -TimeoutSec 2
    $viewerRunning = $null -ne $viewerState.stats.complete_frames
} catch { }
if (-not $viewerRunning) {
    $viewerPython = 'C:\ProgramData\miniconda3\python.exe'
    if (-not (Test-Path -LiteralPath $viewerPython)) {
        $viewerPython = (Get-Command python -ErrorAction Stop).Source
    }
    & $viewerPython -c 'import numpy, serial'
    if ($LASTEXITCODE -ne 0) { throw 'Install dependencies: python -m pip install -r tools/radar_viewer/requirements.txt' }
    $viewerLogs = Join-Path $viewerRoot 'output\live_radar'
    New-Item -ItemType Directory -Force -Path $viewerLogs | Out-Null
    $viewerProcess = Start-Process -FilePath $viewerPython -ArgumentList 'tools/live_radar.py','--connect' -WorkingDirectory $viewerRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $viewerLogs 'server.stdout.log') -RedirectStandardError (Join-Path $viewerLogs 'server.stderr.log')
    $viewerProcess.Id | Set-Content (Join-Path $viewerLogs 'server.pid')
    for ($viewerAttempt = 0; $viewerAttempt -lt 20; $viewerAttempt++) {
        Start-Sleep -Milliseconds 250
        try {
            $viewerState = Invoke-RestMethod "$viewerUrl/api/state?since=0" -TimeoutSec 1
            if ($null -ne $viewerState.stats.complete_frames) { $viewerRunning = $true; break }
        } catch { }
        if ($viewerProcess.HasExited) { break }
    }
    if (-not $viewerRunning) { throw "Viewer did not start. See $viewerLogs\server.stderr.log" }
}
Write-Output "Radar viewer: $viewerUrl"
if (-not $NoBrowser) { Start-Process $viewerUrl }

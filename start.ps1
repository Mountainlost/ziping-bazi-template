$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $env:LOCALAPPDATA 'CodexToolData\bazi-venv\Scripts\python.exe'
$logRoot = Join-Path $env:LOCALAPPDATA 'CodexToolData\bazi\logs'
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run setup.ps1 first' }
foreach ($port in @(8000,3000)) {
    if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
        throw "Port $port is already in use. Existing processes were not changed."
    }
}
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$apiProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m','uvicorn','app.main:app','--app-dir','apps/api','--host','127.0.0.1','--port','8000') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logRoot "$stamp-api.log") -RedirectStandardError (Join-Path $logRoot "$stamp-api-error.log") -PassThru
$webProcess = Start-Process -FilePath (Get-Command node).Source -ArgumentList @('node_modules/next/dist/bin/next','dev','--hostname','127.0.0.1','--port','3000') -WorkingDirectory (Join-Path $projectRoot 'apps\web') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logRoot "$stamp-web.log") -RedirectStandardError (Join-Path $logRoot "$stamp-web-error.log") -PassThru
Write-Host "Started API PID $($apiProcess.Id), Web PID $($webProcess.Id)."
Write-Host 'Open http://127.0.0.1:3000'
Write-Host "To stop: Stop-Process -Id $($apiProcess.Id),$($webProcess.Id)"
Write-Host "Logs: $logRoot"

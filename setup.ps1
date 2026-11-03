$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $env:LOCALAPPDATA 'CodexToolData\bazi-venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    python -m venv (Join-Path $env:LOCALAPPDATA 'CodexToolData\bazi-venv')
    if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed' }
}
& $pythonPath -m pip install -r (Join-Path $projectRoot 'apps\api\requirements.lock.txt')
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed' }
Push-Location (Join-Path $projectRoot 'apps\web')
try {
    npm ci --no-fund --no-audit
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed' }
} finally { Pop-Location }
Write-Host 'Setup complete. Run .\start.ps1'

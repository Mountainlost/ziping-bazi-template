param([Parameter(Mandatory=$true)][string]$ConfigPath)
$ErrorActionPreference = 'Stop'
$config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
$projectRoot = $config.projectRoot
& $config.pythonExecutable -m pip install -r (Join-Path $projectRoot 'apps\api\requirements.lock.txt')
if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed' }
Push-Location (Join-Path $projectRoot 'apps\web')
try {
    npm ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'Frontend installation failed' }
    npm run lint
    if ($LASTEXITCODE -ne 0) { throw 'Lint failed' }
    npm run typecheck
    if ($LASTEXITCODE -ne 0) { throw 'Typecheck failed' }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Production build failed' }
    $destination = Join-Path $projectRoot 'apps\web\.next\standalone\.next\static'
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-Item -Path '.next\static\*' -Destination $destination -Recurse -Force
    New-Item -ItemType Directory -Path '.next\standalone\public' -Force | Out-Null
    Copy-Item -Path 'public\*' -Destination '.next\standalone\public' -Recurse -Force
} finally { Pop-Location }
& $config.pythonExecutable (Join-Path $projectRoot 'deploy\run_server.py') --config $ConfigPath --check
if ($LASTEXITCODE -ne 0) { throw 'Production configuration check failed' }

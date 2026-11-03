param([Parameter(Mandatory=$true)][string]$ServerConfig,[Parameter(Mandatory=$true)][string]$TunnelConfig)
$ErrorActionPreference='Stop'
$ServerConfig=(Resolve-Path -LiteralPath $ServerConfig).Path
$TunnelConfig=(Resolve-Path -LiteralPath $TunnelConfig).Path
$config=Get-Content -LiteralPath $ServerConfig -Raw -Encoding UTF8 | ConvertFrom-Json
New-Item -ItemType Directory -Path $config.logDirectory -Force | Out-Null
foreach($item in @(@{Script='run_server.py';Config=$ServerConfig},@{Script='run_tunnel.py';Config=$TunnelConfig})){
    $scriptPath=Join-Path $config.projectRoot ('deploy\'+$item.Script)
    $owned=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -and $_.CommandLine.Contains($item.Script) -and $_.CommandLine.Contains($item.Config)})
    if($owned.Count){Write-Output ($item.Script+' already running; unchanged.');continue}
    $arguments='-X utf8 "'+$scriptPath+'" --config "'+$item.Config+'"'
    $stamp=Get-Date -Format 'yyyyMMdd-HHmmss'
    $null=Start-Process -FilePath $config.pythonExecutable -ArgumentList $arguments -WorkingDirectory $config.projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $config.logDirectory ($item.Script+'-'+$stamp+'.stdout.log')) -RedirectStandardError (Join-Path $config.logDirectory ($item.Script+'-'+$stamp+'.stderr.log'))
    Write-Output ($item.Script+' started in background.')
}

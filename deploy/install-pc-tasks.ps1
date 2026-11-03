param([Parameter(Mandatory=$true)][string]$ServerConfig,[Parameter(Mandatory=$true)][string]$TunnelConfig)
$ErrorActionPreference='Stop'
$config=Get-Content -LiteralPath $ServerConfig -Raw -Encoding UTF8 | ConvertFrom-Json
& $config.pythonExecutable (Join-Path $config.projectRoot 'deploy\run_server.py') --config $ServerConfig --check
if($LASTEXITCODE -ne 0){throw 'Application configuration check failed'}
& $config.pythonExecutable (Join-Path $config.projectRoot 'deploy\run_tunnel.py') --config $TunnelConfig --check
if($LASTEXITCODE -ne 0){throw 'Tunnel configuration check failed'}
$account=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal=New-ScheduledTaskPrincipal -UserId $account -LogonType Interactive -RunLevel Limited
$trigger=New-ScheduledTaskTrigger -AtLogOn -User $account
$settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 1)
$items=@(@{Name='Ziping-PC-Website';Script='run_server.py';Config=$ServerConfig},@{Name='Ziping-PC-Tunnel';Script='run_tunnel.py';Config=$TunnelConfig})
foreach($item in $items){
    if(Get-ScheduledTask -TaskName $item.Name -ErrorAction SilentlyContinue){throw "Task already exists; left unchanged: $($item.Name)"}
}
foreach($item in $items){
    $scriptPath=Join-Path $config.projectRoot ('deploy\'+$item.Script)
    $arguments='"'+$scriptPath+'" --config "'+$item.Config+'"'
    $action=New-ScheduledTaskAction -Execute $config.pythonExecutable -Argument $arguments -WorkingDirectory $config.projectRoot
    Register-ScheduledTask -TaskName $item.Name -Action $action -Trigger $trigger -Principal $principal -Settings $settings | Out-Null
}
Write-Output 'Two dedicated Ziping tasks registered. Existing tasks unchanged; tasks have not been started.'

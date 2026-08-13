#requires -RunAsAdministrator
# Registra a tarefa que mantem o uvicorn no ar (modo S4U: sem sessao aberta,
# sem senha armazenada). Mesmo padrao ja validado em besc-projects/pedidos-api-besc.
param(
    [string]$AppDir    = 'C:\Users\cloud\pedidos-api-besc\app',
    [string]$RunAsUser = 'supra\cloud',
    [string]$TaskName  = 'pedidos-api-app'
)

$ErrorActionPreference = 'Stop'

$runAppScript = Join-Path $AppDir 'deploy\run-app.ps1'
if (-not (Test-Path $runAppScript)) {
    Write-Output "ERRO: script nao encontrado: $runAppScript"
    exit 1
}

if (-not (Test-Path (Join-Path $AppDir '.env'))) {
    Write-Output "AVISO: .env nao encontrado em $AppDir - a aplicacao vai falhar ao subir."
}

$principal = New-ScheduledTaskPrincipal -UserId $RunAsUser -LogonType S4U -RunLevel Highest
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runAppScript`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Output "Tarefa '$TaskName' ja existe. Recriando..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal `
    -Description 'Mantem a API de pedidos (uvicorn) no ar na porta 9577.' | Out-Null

Write-Output "Tarefa '$TaskName' registrada."
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State | Format-Table -AutoSize | Out-String -Width 200

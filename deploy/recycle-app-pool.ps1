# A API roda sob IIS via httpPlatformHandler (ver web.config): o IIS sobe o
# uvicorn como processo filho e o mantem vivo sozinho. Simplesmente atualizar
# os arquivos no disco NAO faz o IIS recarregar o codigo novo -- e preciso
# reciclar o app pool para que o handler mate o processo velho e suba um novo
# a partir do web.config atualizado.
#
# Isto substitui o antigo restart-service.ps1 (que reiniciava uma Scheduled
# Task numa porta separada, 9577, que nunca foi o processo real por tras do
# site publico em :9579 -- por isso deploys anteriores "funcionavam" sem
# nunca atualizar o que o IIS de fato servia).
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$AppPoolName = 'api-besc-orders'
$HealthUrl   = 'http://localhost:9579/api/dashboard/overview'

$uvLocal = Join-Path $env:USERPROFILE '.local\bin'
if ((Test-Path (Join-Path $uvLocal 'uv.exe')) -and ($env:Path -notlike "*$uvLocal*")) {
    $env:Path = "$uvLocal;$env:Path"
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Output "uv nao encontrado, instalando..."
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$uvLocal;$env:Path"
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Output "ERRO: uv indisponivel apos tentativa de instalacao."
    exit 1
}

Write-Output "Sincronizando dependencias..."
& uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Output "ERRO: uv sync retornou $LASTEXITCODE"
    exit 1
}

Write-Output "Aplicando migrations do Alembic..."
& uv run alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Output "ERRO: alembic upgrade head retornou $LASTEXITCODE"
    exit 1
}

Import-Module WebAdministration -ErrorAction SilentlyContinue
if (-not (Get-Module WebAdministration)) {
    Write-Output "ERRO: modulo WebAdministration indisponivel (IIS/ManagementConsole instalado?)."
    exit 1
}

if (-not (Test-Path "IIS:\AppPools\$AppPoolName")) {
    Write-Output "ERRO: app pool '$AppPoolName' nao existe. Confirme o nome no IIS Manager."
    exit 1
}

Write-Output "Reciclando o app pool '$AppPoolName'..."
Restart-WebAppPool -Name $AppPoolName

# httpPlatformHandler tem startupTimeLimit=60s no web.config; damos a mesma folga.
# 401 conta como "no ar": prova que o FastAPI respondeu, so rejeitou por falta
# de token -- o que e o comportamento correto sem credencial nenhuma.
$deadline = (Get-Date).AddSeconds(60)
$ok = $false
do {
    Start-Sleep -Seconds 3
    try {
        $resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($resp.StatusCode -in 200, 401) { $ok = $true }
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -in 200, 401) { $ok = $true }
    }
} while (-not $ok -and (Get-Date) -lt $deadline)

if ($ok) {
    Write-Output "Deploy OK - $HealthUrl respondendo (app pool no ar)."
} else {
    Write-Output "ATENCAO: $HealthUrl nao respondeu como esperado. Ultimas linhas do log ativo:"
    Get-ChildItem (Join-Path $PWD.Path 'logs') -Filter 'api.log_*' -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1 |
        ForEach-Object { Get-Content $_.FullName -Tail 40 }
    exit 1
}

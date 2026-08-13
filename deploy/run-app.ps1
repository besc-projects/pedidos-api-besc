# Executado pela tarefa agendada 'pedidos-api-app'. Roda o uvicorn em primeiro
# plano: quem mantem o processo vivo e o Agendador de Tarefas, nao a sessao
# que disparou o deploy (que morre junto com a sessao SSH/Actions).
#
# Usa uvicorn direto, nao run.py: run.py tem reload=True (util em dev, mas
# incompativel com um servico de longa duracao gerenciado por tarefa agendada).
param(
    [string]$AppDir = 'C:\Users\cloud\pedidos-api-besc\app',
    [int]   $Port   = 9577
)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

Set-Location $AppDir

$uvLocal = Join-Path $env:USERPROFILE '.local\bin'
if ((Test-Path (Join-Path $uvLocal 'uv.exe')) -and ($env:Path -notlike "*$uvLocal*")) {
    $env:Path = "$uvLocal;$env:Path"
}

# Sem isso, print() com emoji/acentos no codigo da app derruba o processo:
# console do Windows usa cp1252 por padrao, que nao codifica esses caracteres.
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

& uv run uvicorn app.main:app --host 0.0.0.0 --port $Port `
    *> (Join-Path $AppDir 'app.log')

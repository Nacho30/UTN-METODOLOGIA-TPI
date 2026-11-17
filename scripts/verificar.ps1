# Verifica backend, frontend y specs en Windows (PowerShell 5.1+).
# Uso, desde la raiz del repo:
#   powershell -ExecutionPolicy Bypass -File scripts\verificar.ps1
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$fallos = @()

function Paso($titulo) { Write-Host "`n=== $titulo ===" -ForegroundColor Cyan }

Paso "Backend: entorno virtual y dependencias"
Set-Location "$raiz\backend"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -q -r requirements.txt

Paso "Backend: pruebas (unittest)"
& .\.venv\Scripts\python.exe -m unittest discover -s tests -t .
if ($LASTEXITCODE -ne 0) { $fallos += "backend" }

Paso "Frontend: dependencias"
Set-Location "$raiz\frontend"
npm install --no-fund --no-audit
if ($LASTEXITCODE -ne 0) { $fallos += "npm install" }

Paso "Frontend: pruebas"
npm test
if ($LASTEXITCODE -ne 0) { $fallos += "frontend test" }

Paso "Frontend: compilacion (tsc + vite build)"
npm run build
if ($LASTEXITCODE -ne 0) { $fallos += "frontend build" }

Paso "OpenSpec"
Set-Location $raiz
if (Get-Command openspec -ErrorAction SilentlyContinue) {
    openspec list
    openspec validate --all --strict
    if ($LASTEXITCODE -ne 0) { $fallos += "openspec" }
} else {
    Write-Host "OpenSpec CLI no instalado (npm install -g @fission-ai/openspec). Se omite." -ForegroundColor Yellow
}

Paso "Docker Compose (sintaxis)"
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $env:POSTGRES_PASSWORD = "solo-para-validar"
    $env:ODONTOLOGIA_JWT_SECRETO = "solo-para-validar-la-sintaxis-del-compose"
    docker compose config -q
    if ($LASTEXITCODE -ne 0) { $fallos += "docker compose" } else { Write-Host "docker-compose.yml valido" }
    Remove-Item Env:POSTGRES_PASSWORD, Env:ODONTOLOGIA_JWT_SECRETO
} else {
    Write-Host "Docker no instalado. Se omite." -ForegroundColor Yellow
}

if ($fallos.Count -eq 0) {
    Write-Host "`nTODO OK" -ForegroundColor Green
} else {
    Write-Host "`nFALLO: $($fallos -join ', ')" -ForegroundColor Red
    exit 1
}

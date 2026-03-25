# Setup inicial del repositorio central para Sistema B
# Ejecutar UNA SOLA VEZ por el administrador
# Compatible con Windows (PowerShell 5.1+)

$ErrorActionPreference = "Stop"

Write-Host "=== Setup de repositorio central para Sistema B ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Sistema detectado: Windows"
Write-Host ""

# Pedir datos
$RepoPath = Read-Host "Ruta para el repositorio bare (ej: C:\bp-repo.git)"

if (Test-Path $RepoPath) {
    Write-Host "Error: $RepoPath ya existe." -ForegroundColor Red
    exit 1
}

# Crear repo bare
Write-Host ""
Write-Host "Creando repositorio en: $RepoPath"
git init --bare --initial-branch=main $RepoPath
if ($LASTEXITCODE -ne 0) { exit 1 }

# Crear un repo temporal para inicializar estructura
$TempDir = Join-Path $env:TEMP "bp-setup-$(Get-Random)"
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
Push-Location $TempDir

git init -q
git checkout -b main 2>$null

# Crear estructura de directorios
New-Item -ItemType Directory -Path ".bp-locks" -Force | Out-Null
New-Item -ItemType Directory -Path ".bp-meta" -Force | Out-Null

# Crear archivos iniciales
New-Item -ItemType File -Path ".bp-locks/.gitkeep" -Force | Out-Null
"" | Set-Content -Path ".bp-meta/history.jsonl" -NoNewline
"" | Set-Content -Path ".bp-meta/audit.jsonl" -NoNewline

# .gitattributes para LFS
@"
*.xlsx filter=lfs diff=lfs merge=lfs -text
*.xlsm filter=lfs diff=lfs merge=lfs -text
*.xls filter=lfs diff=lfs merge=lfs -text
*.xlsb filter=lfs diff=lfs merge=lfs -text
"@ | Set-Content -Path ".gitattributes"

# Commit inicial
git add -A
git commit -q -m "Inicializacion de Sistema B"

# Push al bare repo
git remote add origin $RepoPath
git push -q -u origin main

# Limpiar
Pop-Location
Remove-Item -Recurse -Force $TempDir

Write-Host ""
Write-Host "=== Repositorio creado correctamente ===" -ForegroundColor Green
Write-Host ""
Write-Host "Siguiente paso para cada usuario:"
Write-Host "  1. Instalar Sistema B:  pip install sistema-b"
Write-Host "  2. Configurar:          bp setup"
Write-Host "  3. Descargar modelos:   bp get"
Write-Host ""
Write-Host "URL del repositorio: $RepoPath"

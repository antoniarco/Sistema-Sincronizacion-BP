# ╔══════════════════════════════════════════════════════════════════╗
# ║  Sistema B — Instalacion rapida para Windows                    ║
# ║                                                                  ║
# ║  El admin envia este comando al equipo:                          ║
# ║  $t="TOKEN"; irm URL | iex                                      ║
# ╚══════════════════════════════════════════════════════════════════╝

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ── Token recibido como variable $t ───────────────────────────
$GITHUB_TOKEN = if ($t) { $t } elseif ($args[0]) { $args[0] } else { $null }
$GITHUB_OWNER = "antoniarco"

if (-not $GITHUB_TOKEN) {
    Write-Host ""
    Write-Host "  ❌ Falta el token de acceso." -ForegroundColor Red
    Write-Host ""
    Write-Host '  Uso correcto (pide el comando completo a tu admin):' -ForegroundColor Yellow
    Write-Host '  $t="TU_TOKEN"; irm URL | iex' -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$TOOL_REPO = "https://github.com/${GITHUB_OWNER}/Sistema-Sincronizacion-BP.git"
$MODELS_REPO = "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_OWNER}/bp-modelos.git"
$INSTALL_DIR = "$env:TEMP\sistema-b-installer"

Clear-Host
Write-Host ""
Write-Host "  ╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║                                                       ║" -ForegroundColor Cyan
Write-Host "  ║   Sistema B — Instalacion rapida (Windows)            ║" -ForegroundColor Cyan
Write-Host "  ║   Control de versiones para modelos BP                ║" -ForegroundColor Cyan
Write-Host "  ║                                                       ║" -ForegroundColor Cyan
Write-Host "  ╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Este instalador configurara todo lo necesario en tu PC."
Write-Host ""
Read-Host "  Pulsa Enter para continuar"

# ── Paso 1: Python ────────────────────────────────────────────
Write-Host ""
Write-Host "  [1/5] Python..." -ForegroundColor Cyan
$pythonCmd = $null
foreach ($cmd in @("python", "python3")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "(\d+)\.(\d+)") {
            if ([int]$Matches[1] -ge 3 -and [int]$Matches[2] -ge 11) {
                $pythonCmd = $cmd
                Write-Host "  ✓ $ver" -ForegroundColor Green
                break
            }
        }
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  ❌ Python 3.11+ no encontrado." -ForegroundColor Red
    Write-Host "  1. Ve a https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  2. MARCA 'Add Python to PATH' al instalar" -ForegroundColor Yellow
    Write-Host "  3. Vuelve a ejecutar este comando" -ForegroundColor Yellow
    $resp = Read-Host "  Abrir pagina de descarga? (S/N)"
    if ($resp -eq "S" -or $resp -eq "s") { Start-Process "https://www.python.org/downloads/" }
    exit 1
}

# ── Paso 2: Git ───────────────────────────────────────────────
Write-Host "  [2/5] Git..." -ForegroundColor Cyan
try {
    $gitVer = git --version 2>&1
    Write-Host "  ✓ $gitVer" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Git no encontrado." -ForegroundColor Red
    Write-Host "  1. Ve a https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "  2. Instala con opciones por defecto" -ForegroundColor Yellow
    $resp = Read-Host "  Abrir pagina de descarga? (S/N)"
    if ($resp -eq "S" -or $resp -eq "s") { Start-Process "https://git-scm.com/download/win" }
    exit 1
}

# ── Paso 3: pipx ─────────────────────────────────────────────
Write-Host "  [3/5] pipx..." -ForegroundColor Cyan
$pipxCmd = "pipx"
try {
    & pipx --version 2>&1 | Out-Null
    Write-Host "  ✓ ya instalado" -ForegroundColor Green
} catch {
    Write-Host "  Instalando pipx..."
    & $pythonCmd -m pip install --user pipx 2>&1 | Out-Null
    & $pythonCmd -m pipx ensurepath 2>&1 | Out-Null
    $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
    try { & pipx --version 2>&1 | Out-Null; Write-Host "  ✅ pipx instalado" -ForegroundColor Green }
    catch { $pipxCmd = "$pythonCmd -m pipx"; Write-Host "  ✅ pipx (via python -m)" -ForegroundColor Green }
}

# ── Paso 4: Descargar e instalar ─────────────────────────────
Write-Host "  [4/5] Descargando Sistema B..." -ForegroundColor Cyan
if (Test-Path $INSTALL_DIR) { Remove-Item -Recurse -Force $INSTALL_DIR }
git clone --depth 1 $TOOL_REPO $INSTALL_DIR 2>&1 | Out-Null
if (-not (Test-Path "$INSTALL_DIR\pyproject.toml")) {
    Write-Host "  ❌ No se pudo descargar" -ForegroundColor Red; exit 1
}
if ($pipxCmd -eq "pipx") { & pipx install $INSTALL_DIR --force 2>&1 | Out-Null }
else { & $pythonCmd -m pipx install $INSTALL_DIR --force 2>&1 | Out-Null }
$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction SilentlyContinue
try { & bp --help 2>&1 | Out-Null; Write-Host "  ✅ Sistema B instalado" -ForegroundColor Green }
catch { Write-Host "  ❌ Error instalando 'bp'" -ForegroundColor Red; exit 1 }

# ── Paso 5: Configuracion ────────────────────────────────────
Write-Host ""
Write-Host "  [5/5] Configuracion" -ForegroundColor Cyan
$configDir = "$env:APPDATA\bp"
if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Path $configDir -Force | Out-Null }
$configFile = "$configDir\config.toml"
if (-not (Test-Path $configFile)) {
    @"
[user]
nombre = ""
email = ""
rol = "user"

[repositorio]
url = "$MODELS_REPO"
workspace = "$env:USERPROFILE\bp-workspace"

[slack]
webhook_url = ""
canal = "#finance-bp-control"
activado = false

[bloqueo]
expiracion_horas = 24
auto_liberar_tras_push = true
"@ | Set-Content -Path $configFile -Encoding UTF8
}

Write-Host ""
Write-Host "  Responde las siguientes preguntas:" -ForegroundColor White
Write-Host "  (La conexion al repositorio ya esta configurada)" -ForegroundColor Yellow
Write-Host ""
& bp setup

# ── Fin ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║   ✅ Sistema B instalado correctamente                ║" -ForegroundColor Green
Write-Host "  ║                                                       ║" -ForegroundColor Green
Write-Host "  ║   Para empezar:                                       ║" -ForegroundColor Green
Write-Host "  ║     1. Cierra y abre una nueva PowerShell             ║" -ForegroundColor Green
Write-Host "  ║     2. Escribe: bp web                                ║" -ForegroundColor Green
Write-Host "  ╚═══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

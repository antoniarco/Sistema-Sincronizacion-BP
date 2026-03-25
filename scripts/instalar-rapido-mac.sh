#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  Sistema B — Instalacion rapida para macOS                      ║
# ║                                                                  ║
# ║  Pega esto en Terminal:                                          ║
# ║  curl -fsSL URL_DEL_SCRIPT | bash                               ║
# ╚══════════════════════════════════════════════════════════════════╝

set -e

# ── Configuracion (el admin rellena esto una vez) ─────────────
GITHUB_TOKEN="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"
GITHUB_OWNER="antoniarco"

# Repo del TOOL (sistema-b) — se descarga con gh auth o HTTPS publico
TOOL_REPO="https://github.com/${GITHUB_OWNER}/Sistema-Sincronizacion-BP.git"
# Repo de los MODELOS BP — acceso via token (privado)
MODELS_REPO="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_OWNER}/bp-modelos.git"

INSTALL_DIR="$HOME/.sistema-b-installer"
# ──────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}║   ${BOLD}Sistema B${NC}${CYAN} — Instalacion rapida (macOS)             ║${NC}"
echo -e "${CYAN}║   Control de versiones para modelos BP                ║${NC}"
echo -e "${CYAN}║                                                       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Este instalador configurara todo lo necesario en tu Mac."
echo -e "  Solo tienes que responder unas preguntas al final."
echo ""
echo -e "  ${YELLOW}Pulsa Enter para continuar o Ctrl+C para cancelar...${NC}"
read -r

# ── Funciones ─────────────────────────────────────────────────

paso() { echo ""; echo -e "  ${CYAN}[$1/6]${NC} ${BOLD}$2${NC}"; }
ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
skip() { echo -e "  ${GREEN}✓ $1 (ya instalado)${NC}"; }
fail() { echo -e "  ${RED}❌ $1${NC}"; echo -e "  ${YELLOW}$2${NC}"; echo ""; echo "  Pulsa Enter para cerrar..."; read -r; exit 1; }

# ── Paso 1: Homebrew ──────────────────────────────────────────

paso "1" "Comprobando Homebrew..."
if command -v brew &>/dev/null; then
    skip "Homebrew encontrado"
else
    echo -e "  Instalando Homebrew... ${YELLOW}(puede pedir tu contraseña)${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    [ -f /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)" && echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    [ -f /usr/local/bin/brew ] && eval "$(/usr/local/bin/brew shellenv)"
    command -v brew &>/dev/null && ok "Homebrew instalado" || fail "No se pudo instalar Homebrew" "Visita https://brew.sh"
fi

# ── Paso 2: Python ────────────────────────────────────────────

paso "2" "Comprobando Python..."
PY_OK=false
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$($cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=$(echo "$ver" | cut -d. -f1); minor=$(echo "$ver" | cut -d. -f2)
        [ "$major" -ge 3 ] && [ "$minor" -ge 11 ] && PY_OK=true && skip "Python $ver" && break
    fi
done
if [ "$PY_OK" = false ]; then
    brew install python@3.13 && ok "Python instalado" || fail "No se pudo instalar Python" "Ejecuta: brew install python@3.13"
fi

# ── Paso 3: Git ───────────────────────────────────────────────

paso "3" "Comprobando Git..."
if command -v git &>/dev/null; then
    skip "Git $(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"
else
    brew install git && ok "Git instalado" || fail "No se pudo instalar Git" "Ejecuta: brew install git"
fi

# ── Paso 4: pipx ─────────────────────────────────────────────

paso "4" "Comprobando pipx..."
if command -v pipx &>/dev/null; then
    skip "pipx encontrado"
else
    brew install pipx && pipx ensurepath 2>/dev/null && export PATH="$HOME/.local/bin:$PATH"
    command -v pipx &>/dev/null && ok "pipx instalado" || fail "No se pudo instalar pipx" "Ejecuta: brew install pipx"
fi

# ── Paso 5: Descargar e instalar Sistema B ────────────────────

paso "5" "Descargando e instalando Sistema B..."
rm -rf "$INSTALL_DIR"
git clone --depth 1 "$TOOL_REPO" "$INSTALL_DIR" 2>/dev/null
[ ! -f "$INSTALL_DIR/pyproject.toml" ] && fail "No se pudo descargar Sistema B" "Verifica tu conexion a internet"

pipx install "$INSTALL_DIR" --force 2>/dev/null
export PATH="$HOME/.local/bin:$PATH"
command -v bp &>/dev/null && ok "Sistema B instalado" || fail "No se pudo instalar el comando 'bp'" ""

rm -rf "$INSTALL_DIR"

# ── Paso 6: Configuracion automatica ─────────────────────────

paso "6" "Configurando Sistema B..."
echo ""
echo -e "  ${BOLD}Responde las siguientes preguntas:${NC}"
echo -e "  ${YELLOW}(La URL del repositorio ya esta preconfigurada)${NC}"
echo ""

# Pre-crear config con el repo ya configurado para que bp setup lo use como default
CONFIG_DIR="$HOME/.config/bp"
mkdir -p "$CONFIG_DIR"

# Solo pre-configurar si no existe config
if [ ! -f "$CONFIG_DIR/config.toml" ]; then
    cat > "$CONFIG_DIR/config.toml" << TOML
[user]
nombre = ""
email = ""
rol = "user"

[repositorio]
url = "${MODELS_REPO}"
workspace = "$HOME/bp-workspace"

[slack]
webhook_url = ""
canal = "#finance-bp-control"
activado = false

[bloqueo]
expiracion_horas = 24
auto_liberar_tras_push = true
TOML
fi

bp setup

# ── Fin ───────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}║   ✅ Sistema B instalado correctamente                ║${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}║   Para empezar:                                       ║${NC}"
echo -e "${GREEN}║     1. Cierra y abre una nueva Terminal               ║${NC}"
echo -e "${GREEN}║     2. Escribe: bp web                                ║${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

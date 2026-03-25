#!/usr/bin/env bash
# ╔═══════════════════════════════════════════════════════════════╗
# ║  Sistema B — Instalador automatico para macOS               ║
# ║  Haz doble clic en este archivo para instalar               ║
# ╚═══════════════════════════════════════════════════════════════╝

set -e

# ── Configuracion del acceso ──────────────────────────────────
# ADMIN: Pon aqui el token antes de enviar el .zip al equipo
GITHUB_TOKEN="${BP_TOKEN:-PEGA_TU_TOKEN_AQUI}"
GITHUB_OWNER="antoniarco"
MODELS_REPO="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_OWNER}/bp-modelos.git"
# ──────────────────────────────────────────────────────────────

# Colores
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
echo -e "${CYAN}║   ${BOLD}Sistema B${NC}${CYAN} — Instalador para macOS                  ║${NC}"
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

paso() {
    echo ""
    echo -e "  ${CYAN}[$1/6]${NC} ${BOLD}$2${NC}"
}

ok() {
    echo -e "  ${GREEN}✅ $1${NC}"
}

skip() {
    echo -e "  ${GREEN}✓ $1 (ya instalado)${NC}"
}

fail() {
    echo -e "  ${RED}❌ $1${NC}"
    echo -e "  ${YELLOW}$2${NC}"
    echo ""
    echo -e "  Pulsa Enter para cerrar..."
    read -r
    exit 1
}

# ── Paso 1: Homebrew ──────────────────────────────────────────

paso "1" "Comprobando Homebrew..."

if command -v brew &>/dev/null; then
    skip "Homebrew encontrado"
else
    echo -e "  Homebrew no esta instalado. Instalando..."
    echo -e "  ${YELLOW}(puede pedirte la contraseña del Mac)${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Añadir Homebrew al PATH (Apple Silicon y Intel)
    if [ -f /opt/homebrew/bin/brew ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    elif [ -f /usr/local/bin/brew ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi

    if command -v brew &>/dev/null; then
        ok "Homebrew instalado"
    else
        fail "No se pudo instalar Homebrew" "Visita https://brew.sh para instalarlo manualmente"
    fi
fi

# ── Paso 2: Python ────────────────────────────────────────────

paso "2" "Comprobando Python..."

PYTHON_OK=false
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PY_VERSION=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
            PYTHON_CMD="$cmd"
            PYTHON_OK=true
            skip "Python $PY_VERSION encontrado"
            break
        fi
    fi
done

if [ "$PYTHON_OK" = false ]; then
    echo -e "  Python 3.11+ no encontrado. Instalando..."
    brew install python@3.13
    PYTHON_CMD="python3"
    if $PYTHON_CMD --version &>/dev/null; then
        ok "Python instalado"
    else
        fail "No se pudo instalar Python" "Ejecuta: brew install python@3.13"
    fi
fi

# ── Paso 3: Git ───────────────────────────────────────────────

paso "3" "Comprobando Git..."

if command -v git &>/dev/null; then
    skip "Git $(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"
else
    echo -e "  Git no encontrado. Instalando..."
    brew install git
    if command -v git &>/dev/null; then
        ok "Git instalado"
    else
        fail "No se pudo instalar Git" "Ejecuta: brew install git"
    fi
fi

# ── Paso 4: pipx ─────────────────────────────────────────────

paso "4" "Comprobando pipx..."

if command -v pipx &>/dev/null; then
    skip "pipx encontrado"
else
    echo -e "  pipx no encontrado. Instalando..."
    brew install pipx
    pipx ensurepath 2>/dev/null
    export PATH="$HOME/.local/bin:$PATH"
    if command -v pipx &>/dev/null; then
        ok "pipx instalado"
    else
        fail "No se pudo instalar pipx" "Ejecuta: brew install pipx"
    fi
fi

# ── Paso 5: Sistema B ────────────────────────────────────────

paso "5" "Instalando Sistema B..."

# Determinar la ruta del paquete (mismo directorio que este script)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKAGE_DIR="$(dirname "$SCRIPT_DIR")"

# Verificar que pyproject.toml existe
if [ ! -f "$PACKAGE_DIR/pyproject.toml" ]; then
    fail "No se encontro el paquete de Sistema B" "Asegurate de que este archivo esta dentro de la carpeta scripts/ del proyecto"
fi

pipx install "$PACKAGE_DIR" --force 2>/dev/null
export PATH="$HOME/.local/bin:$PATH"

if command -v bp &>/dev/null; then
    ok "Sistema B instalado correctamente"
else
    fail "No se pudo instalar Sistema B" "Intenta manualmente: pipx install \"$PACKAGE_DIR\""
fi

# ── Paso 6: Configuracion ────────────────────────────────────

paso "6" "Configurando Sistema B..."

# Pre-configurar el repo con token para que el usuario no tenga que tocarlo
CONFIG_DIR="$HOME/.config/bp"
mkdir -p "$CONFIG_DIR"
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

echo ""
echo -e "  ${BOLD}Responde las siguientes preguntas:${NC}"
echo -e "  ${YELLOW}(La URL del repositorio ya esta preconfigurada)${NC}"
echo ""

bp setup

# ── Fin ───────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}║   ✅ Sistema B instalado correctamente                ║${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}║   Para empezar:                                       ║${NC}"
echo -e "${GREEN}║     • Abre Terminal y escribe: bp web                 ║${NC}"
echo -e "${GREEN}║     • O directamente: bp get                          ║${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${YELLOW}Nota: si 'bp' no se reconoce, cierra y abre Terminal.${NC}"
echo ""
echo -e "  Pulsa Enter para cerrar..."
read -r

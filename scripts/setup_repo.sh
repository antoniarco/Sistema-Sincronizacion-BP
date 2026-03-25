#!/usr/bin/env bash
# Setup inicial del repositorio central para Sistema B
# Ejecutar UNA SOLA VEZ por el administrador
# Compatible con macOS y Linux

set -euo pipefail

echo "=== Setup de repositorio central para Sistema B ==="
echo ""
echo "Sistema detectado: $(uname -s)"
echo ""

# Pedir datos
read -rp "Ruta para el repositorio bare (ej: /srv/bp-repo.git): " REPO_PATH
REPO_PATH="${REPO_PATH/#\~/$HOME}"  # Expandir ~

if [ -d "$REPO_PATH" ]; then
    echo "Error: $REPO_PATH ya existe."
    exit 1
fi

# Crear repo bare
echo ""
echo "Creando repositorio en: $REPO_PATH"
git init --bare --initial-branch=main "$REPO_PATH"

# Crear un repo temporal para inicializar estructura
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"
git init -q
git checkout -b main 2>/dev/null || git switch -c main

# Crear estructura de directorios
mkdir -p .bp-locks .bp-meta

# Crear archivos iniciales
touch .bp-locks/.gitkeep
echo '' > .bp-meta/history.jsonl
echo '' > .bp-meta/audit.jsonl

# .gitattributes para LFS (si esta disponible)
cat > .gitattributes << 'GITATTR'
*.xlsx filter=lfs diff=lfs merge=lfs -text
*.xlsm filter=lfs diff=lfs merge=lfs -text
*.xls filter=lfs diff=lfs merge=lfs -text
*.xlsb filter=lfs diff=lfs merge=lfs -text
GITATTR

# Commit inicial
git add -A
git commit -q -m "Inicializacion de Sistema B"

# Push al bare repo
git remote add origin "$REPO_PATH"
git push -q -u origin main

# Limpiar
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "=== Repositorio creado correctamente ==="
echo ""
echo "Siguiente paso para cada usuario:"
echo "  1. Instalar Sistema B:  pip install sistema-b"
echo "  2. Configurar:          bp setup"
echo "  3. Descargar modelos:   bp get"
echo ""
echo "URL del repositorio: $REPO_PATH"

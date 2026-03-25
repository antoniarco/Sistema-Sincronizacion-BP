@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ╔═══════════════════════════════════════════════════════════════╗
:: ║  Sistema B — Instalador automatico para Windows              ║
:: ║  Haz doble clic en este archivo para instalar                ║
:: ╚═══════════════════════════════════════════════════════════════╝

:: ── Configuracion del acceso ─────────────────────────────────
:: ADMIN: Pon aqui el token antes de enviar el .zip al equipo
set "GITHUB_TOKEN=PEGA_TU_TOKEN_AQUI"
set "GITHUB_OWNER=antoniarco"
set "MODELS_REPO=https://x-access-token:!GITHUB_TOKEN!@github.com/!GITHUB_OWNER!/bp-modelos.git"
:: ─────────────────────────────────────────────────────────────

cls
echo.
echo   ╔═══════════════════════════════════════════════════════╗
echo   ║                                                       ║
echo   ║   Sistema B — Instalador para Windows                 ║
echo   ║   Control de versiones para modelos BP                ║
echo   ║                                                       ║
echo   ╚═══════════════════════════════════════════════════════╝
echo.
echo   Este instalador configurara todo lo necesario en tu PC.
echo   Solo tienes que responder unas preguntas al final.
echo.
pause

:: ── Paso 1: Python ───────────────────────────────────────────

echo.
echo   [1/5] Comprobando Python...

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
    echo   ✓ Python !PY_VER! encontrado
    goto :check_python_version
) else (
    goto :no_python
)

:check_python_version
:: Extraer version mayor y menor
for /f "tokens=1,2 delims=." %%a in ("!PY_VER!") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)
if !PY_MAJOR! GEQ 3 if !PY_MINOR! GEQ 11 goto :python_ok

:no_python
echo.
echo   ❌ Python 3.11 o superior no encontrado.
echo.
echo   INSTRUCCIONES:
echo   1. Ve a https://www.python.org/downloads/
echo   2. Descarga Python 3.13 o superior
echo   3. IMPORTANTE: Marca "Add Python to PATH" al instalar
echo   4. Una vez instalado, vuelve a ejecutar este archivo
echo.
pause
exit /b 1

:python_ok

:: ── Paso 2: Git ──────────────────────────────────────────────

echo.
echo   [2/5] Comprobando Git...

where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=3" %%i in ('git --version') do echo   ✓ Git %%i encontrado
    goto :git_ok
)

echo.
echo   ❌ Git no encontrado.
echo.
echo   INSTRUCCIONES:
echo   1. Ve a https://git-scm.com/download/win
echo   2. Descarga e instala Git (usa opciones por defecto)
echo   3. Una vez instalado, vuelve a ejecutar este archivo
echo.
pause
exit /b 1

:git_ok

:: ── Paso 3: pipx ────────────────────────────────────────────

echo.
echo   [3/5] Comprobando pipx...

where pipx >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ✓ pipx encontrado
    goto :pipx_ok
)

echo   pipx no encontrado. Instalando...
python -m pip install --user pipx >nul 2>&1
python -m pipx ensurepath >nul 2>&1

:: Actualizar PATH para esta sesion
for /f "tokens=*" %%i in ('python -c "import site; print(site.getusersitepackages().replace(chr(92)+chr(39)Lib'+chr(92)+'site-packages',chr(92)+'Scripts'))"') do set "PIPX_BIN=%%i"
set "PATH=%USERPROFILE%\.local\bin;%PIPX_BIN%;%PATH%"

where pipx >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ✅ pipx instalado
    goto :pipx_ok
)

:: Fallback: intentar con python -m pipx
echo   Usando python -m pipx como alternativa...
set "PIPX_CMD=python -m pipx"
goto :install_sb

:pipx_ok
set "PIPX_CMD=pipx"

:: ── Paso 4: Sistema B ───────────────────────────────────────

:install_sb
echo.
echo   [4/5] Instalando Sistema B...

:: Determinar la ruta del paquete (carpeta padre de scripts\)
set "SCRIPT_DIR=%~dp0"
set "PACKAGE_DIR=%SCRIPT_DIR%..\"

:: Verificar que pyproject.toml existe
if not exist "%PACKAGE_DIR%pyproject.toml" (
    echo.
    echo   ❌ No se encontro el paquete de Sistema B.
    echo   Asegurate de que este archivo esta dentro de scripts\ del proyecto.
    echo.
    pause
    exit /b 1
)

%PIPX_CMD% install "%PACKAGE_DIR%" --force >nul 2>&1

:: Actualizar PATH
set "PATH=%USERPROFILE%\.local\bin;%PATH%"

where bp >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Sistema B instalado correctamente
    goto :setup
)

:: Si bp no se encuentra, intentar con la ruta completa de pipx
echo   ⚠ bp no encontrado en PATH. Verificando instalacion...
if exist "%USERPROFILE%\.local\bin\bp.exe" (
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    echo   ✅ Sistema B instalado (en %USERPROFILE%\.local\bin\)
    goto :setup
)

echo.
echo   ❌ No se pudo instalar Sistema B.
echo   Intenta manualmente: pipx install "%PACKAGE_DIR%"
echo.
pause
exit /b 1

:: ── Paso 5: Configuracion ───────────────────────────────────

:setup
echo.
echo   [5/5] Configurando Sistema B...

:: Pre-configurar el repo con token
set "CONFIG_DIR=%APPDATA%\bp"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
if not exist "%CONFIG_DIR%\config.toml" (
    (
        echo [user]
        echo nombre = ""
        echo email = ""
        echo rol = "user"
        echo.
        echo [repositorio]
        echo url = "!MODELS_REPO!"
        echo workspace = "%USERPROFILE%\bp-workspace"
        echo.
        echo [slack]
        echo webhook_url = ""
        echo canal = "#finance-bp-control"
        echo activado = false
        echo.
        echo [bloqueo]
        echo expiracion_horas = 24
        echo auto_liberar_tras_push = true
    ) > "%CONFIG_DIR%\config.toml"
)

echo.
echo   Responde las siguientes preguntas:
echo   (La URL del repositorio ya esta preconfigurada)
echo.

bp setup

:: ── Fin ──────────────────────────────────────────────────────

echo.
echo   ╔═══════════════════════════════════════════════════════╗
echo   ║                                                       ║
echo   ║   ✅ Sistema B instalado correctamente                ║
echo   ║                                                       ║
echo   ║   Para empezar:                                       ║
echo   ║     * Abre una terminal y escribe: bp web             ║
echo   ║     * O directamente: bp get                          ║
echo   ║                                                       ║
echo   ╚═══════════════════════════════════════════════════════╝
echo.
echo   Nota: si 'bp' no se reconoce, cierra y abre la terminal.
echo.
pause

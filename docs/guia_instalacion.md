# Sistema B — Guia de instalacion

## Que es Sistema B

Sistema B es una herramienta para que tu equipo de finanzas pueda trabajar con modelos BP (Business Plans) en local de forma segura. Permite:

- Descargar la ultima version de un modelo
- Reservarlo para que nadie lo modifique mientras trabajas
- Subir tus cambios con un comentario
- Ver quien esta trabajando en cada modelo
- Recibir avisos por Slack

Tiene dos formas de usarse:
- **Interfaz web** (recomendada): abre una pagina en tu navegador con botones
- **Terminal**: comandos rapidos como `bp get`, `bp lock`, `bp push`

---

## Instalacion en un comando (recomendado)

Pega un solo comando en la terminal y el sistema se descarga, instala y configura automaticamente.

### macOS

Abre **Terminal** (busca "Terminal" en Spotlight) y pega:

```bash
curl -fsSL https://raw.githubusercontent.com/antoniarco/Sistema-Sincronizacion-BP/main/scripts/instalar-rapido-mac.sh | bash
```

### Windows

Abre **PowerShell** (busca "PowerShell" en el menu Inicio) y pega:

```powershell
irm https://raw.githubusercontent.com/antoniarco/Sistema-Sincronizacion-BP/main/scripts/instalar-rapido-windows.ps1 | iex
```

### Que hace este comando

El instalador automaticamente:

1. Comprueba si tienes Python, Git y pipx (y los instala si faltan)
2. Descarga Sistema B desde GitHub
3. Instala el comando `bp` de forma global
4. Lanza el asistente de configuracion (`bp setup`)

Al terminar, cierra y abre la terminal y escribe `bp web` para empezar.

> **Nota para el admin**: cambia `antoniarco` en las URLs por tu organizacion o usuario de GitHub real antes de enviar estos comandos a tu equipo.

---

## Instalacion con el archivo ZIP (alternativa)

Si no puedes usar el comando de arriba, el administrador te enviara la carpeta `sistema-b` comprimida (.zip).

### macOS

1. Descomprime el archivo .zip
2. Abre la carpeta `sistema-b/scripts/`
3. Haz **doble clic** en `instalar-mac.command`
4. Se abrira una terminal que lo instala todo
5. Al final te pedira tus datos (nombre, email, repositorio)
6. Listo

> Si macOS dice "no se puede abrir porque es de un desarrollador no identificado": clic derecho > Abrir > Abrir.

### Windows

1. Descomprime el archivo .zip
2. Abre la carpeta `sistema-b\scripts\`
3. Haz **doble clic** en `instalar-windows.bat`
4. Se abrira una ventana que comprueba los requisitos
5. Si falta Python o Git, te dara las instrucciones para instalarlos
6. Al final te pedira tus datos (nombre, email, repositorio)
7. Listo

> Si Windows muestra un aviso de seguridad: "Mas informacion" > "Ejecutar de todas formas".

---

## Instalacion manual (avanzado)

Si prefieres instalar paso a paso.

### Requisitos previos

#### Python 3.11 o superior

**macOS:**
```bash
brew install python@3.13
```

**Windows:**
- Descarga desde https://www.python.org/downloads/
- **IMPORTANTE**: marca la casilla "Add Python to PATH" durante la instalacion

**Linux:**
```bash
sudo apt install python3 python3-pip   # Ubuntu/Debian
```

**Comprobar:** `python3 --version` (macOS/Linux) o `python --version` (Windows). Debe ser 3.11+.

#### Git

**macOS:**
```bash
brew install git
```

**Windows:**
- Descarga desde https://git-scm.com/download/win

**Linux:**
```bash
sudo apt install git
```

**Comprobar:** `git --version`

#### pipx

**macOS:**
```bash
brew install pipx && pipx ensurepath
```

**Windows:**
```bash
pip install pipx && pipx ensurepath
```

**Linux:**
```bash
pip3 install pipx && pipx ensurepath
```

> Tras instalar pipx, **cierra y vuelve a abrir la terminal**.

### Instalar Sistema B

```bash
# Desde GitHub
pipx install git+https://github.com/antoniarco/Sistema-Sincronizacion-BP.git

# O desde una carpeta local
pipx install /ruta/a/sistema-b          # macOS/Linux
pipx install C:\ruta\a\sistema-b        # Windows
```

### Configurar

```bash
bp setup
```

Te pedira estos datos (el admin te los dara):

| Pregunta | Que poner | Ejemplo |
|----------|-----------|---------|
| Nombre completo | Tu nombre real | Maria Lopez |
| Email | Tu email de trabajo | maria.lopez@empresa.com |
| Rol | `user` (normal) o `admin` | user |
| URL del repositorio | Te la dara el admin | git@github.com:empresa/bp-modelos.git |
| Carpeta de trabajo | Donde guardar los archivos | ~/bp-workspace |
| Webhook de Slack | Te lo dara el admin (opcional) | https://hooks.slack.com/services/... |
| Canal de Slack | Canal para avisos | #finance-bp-control |
| Expiracion reservas | Horas antes de que expire | 24 |
| Auto-liberar | Liberar reserva al subir | si |

### Descargar modelos

```bash
bp get
```

---

## Primer uso

### Opcion A: Interfaz web (recomendada para usuarios no tecnicos)

Abre una terminal y escribe:

```bash
bp web
```

Se abrira tu navegador en `http://localhost:8000` con esta interfaz:

```
┌──────────────────────────────────────────────────────────┐
│  Sistema B                              👤 Ana Garcia    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📄 BP_Anual.xlsx       ✅ Al dia  ·  🔓 Libre         │
│     [🔒 Reservar] [📂 Abrir en Excel] [⬇️ Descargar]   │
│                                                          │
│  📄 BP_Q1.xlsx          ✏️ Con cambios · 🔒 Por ti      │
│     [📤 Subir cambios] [🔓 Liberar] [📂 Abrir]         │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  📜 Historial reciente                                   │
│  v3  Ana  "ajuste EBITDA"                25/03 13:15    │
│  v2  Carlos  "nuevo escenario"           24/03 10:30    │
└──────────────────────────────────────────────────────────┘
```

Desde aqui puedes:
- Ver el estado de cada modelo (al dia, con cambios, reservado)
- Reservar y liberar modelos con un clic
- Subir cambios con un comentario
- Abrir archivos directamente en Excel
- Descargar archivos a tu carpeta de Descargas
- Cambiar los ajustes (boton ⚙️ Ajustes arriba)

> **Tip**: deja la terminal abierta mientras usas la interfaz web. Para cerrarla, pulsa `Ctrl+C`.

### Opcion B: Terminal

```bash
bp get                              # Descarga la ultima version
bp status                           # Ve el estado de tus modelos
bp lock BP_Anual.xlsx               # Reserva un modelo
# ... edita el archivo en Excel ...
bp push "ajuste escenario base"     # Sube tus cambios
```

---

## Flujo de trabajo dia a dia

### Con la interfaz web

1. Abre una terminal y escribe `bp web`
2. Haz clic en **📥 Actualizar modelos**
3. Haz clic en **🔒 Reservar** en el modelo que quieras editar
4. Haz clic en **📂 Abrir en Excel** para editarlo
5. Cuando termines, haz clic en **📤 Subir cambios** y escribe un comentario
6. La reserva se libera automaticamente

### Con la terminal

```
1. bp get                           → Descarga la ultima version
2. bp lock BP_Anual.xlsx            → Reserva el modelo
3. (Edita el archivo en Excel)
4. bp push "tu comentario"          → Sube tus cambios
```

---

## Referencia rapida de comandos

| Comando | Que hace |
|---------|----------|
| `bp` | Muestra el panel de ayuda con todos los comandos |
| `bp web` | Abre la interfaz visual en el navegador |
| `bp get` | Descarga la ultima version de los modelos |
| `bp status` | Muestra el estado de cada modelo |
| `bp lock modelo.xlsx` | Reserva un modelo para trabajar |
| `bp unlock modelo.xlsx` | Libera un modelo sin subir cambios |
| `bp push "comentario"` | Sube tus cambios con un comentario |
| `bp who modelo.xlsx` | Mira quien tiene reservado un modelo |
| `bp history` | Consulta el historial de versiones |
| `bp setup` | Cambia tu configuracion |
| `bp force-unlock modelo.xlsx` | [Admin] Fuerza la liberacion de una reserva |
| `bp revert 3 modelo.xlsx` | [Admin] Restaura la version 3 de un modelo |
| `bp logs` | [Admin] Ve acciones administrativas |

---

## Donde estan mis archivos

| Que | macOS / Linux | Windows |
|-----|---------------|---------|
| Tus modelos Excel | `~/bp-workspace/` | `C:\Users\TuUsuario\bp-workspace\` |
| Tu configuracion | `~/.config/bp/config.toml` | `%APPDATA%\bp\config.toml` |
| Datos internos (no tocar) | `~/bp-workspace/.bp/` | `bp-workspace\.bp\` |

La carpeta de trabajo se configura durante `bp setup` y se puede cambiar en cualquier momento desde la interfaz web (⚙️ Ajustes).

> **IMPORTANTE**: edita los archivos Excel directamente en la carpeta de trabajo. No los copies a otra ubicacion: el sistema necesita detectar los cambios en esa carpeta.

---

## Ajustes

Puedes cambiar la configuracion de tres formas:

### Desde la interfaz web (mas facil)
1. Ejecuta `bp web`
2. Haz clic en **⚙️ Ajustes** (arriba)
3. Modifica los campos
4. Haz clic en **💾 Guardar cambios**

### Desde la terminal
```bash
bp setup
```

### Editando el archivo directamente

- **macOS/Linux**: `~/.config/bp/config.toml`
- **Windows**: `%APPDATA%\bp\config.toml`

```toml
[user]
nombre = "Maria Lopez"
email = "maria.lopez@empresa.com"
rol = "user"                          # "user" o "admin"

[repositorio]
url = "git@github.com:empresa/bp-modelos.git"
workspace = "~/bp-workspace"          # donde se guardan tus archivos

[slack]
webhook_url = "https://hooks.slack.com/services/..."
canal = "#finance-bp-control"
activado = true

[bloqueo]
expiracion_horas = 24                 # horas antes de que expire una reserva
auto_liberar_tras_push = true         # liberar reserva al subir cambios
```

---

## Problemas frecuentes

### "No se encontro el espacio de trabajo"
Ejecuta `bp get` para descargar los modelos por primera vez.

### "Sistema B no esta configurado"
Ejecuta `bp setup` para configurar tu entorno.

### "No puedes subir cambios sin reservar el modelo"
Reserva primero: `bp lock modelo.xlsx` o haz clic en "🔒 Reservar" en la web.

### "Tu copia esta desactualizada"
Alguien subio una version nueva. Ejecuta `bp get` o haz clic en "📥 Actualizar modelos" en la web.

### "El modelo esta reservado por otra persona"
Espera a que termine o contactala. Si quedo huerfano, un admin puede hacer clic en "⚡ Forzar liberacion" o ejecutar `bp force-unlock modelo.xlsx`.

### "No se pudo conectar con el repositorio"
Verifica tu conexion a internet. Si usas SSH, comprueba las claves: `ssh -T git@github.com`.

### La interfaz web no abre
- Comprueba que la terminal siga abierta con `bp web` ejecutandose
- Abre manualmente `http://localhost:8000` en tu navegador
- Puerto ocupado: `bp web --port 9000`

### El instalador de macOS dice "desarrollador no identificado"
Clic derecho en el archivo > Abrir > Abrir. Solo la primera vez.

### El instalador de Windows muestra aviso de seguridad
Haz clic en "Mas informacion" > "Ejecutar de todas formas".

### El comando `bp` no se reconoce tras instalar
Cierra y vuelve a abrir la terminal. Si sigue sin funcionar: `pipx ensurepath` y reabrir.

### PowerShell no permite ejecutar scripts
Ejecuta primero: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y luego vuelve a intentar.

---

## Actualizar Sistema B

**Si instalaste con el comando rapido:** vuelve a ejecutar el mismo comando. Detectara que ya tienes todo y solo actualizara Sistema B.

**Si instalaste con el .zip:** vuelve a ejecutar el instalador (.command o .bat) con la nueva version.

**Si instalaste manualmente:**
```bash
pipx install /ruta/a/sistema-b --force
```

---

## Desinstalar

```bash
pipx uninstall sistema-b
```

Esto elimina el comando `bp` y la interfaz web. Tus archivos Excel en la carpeta de trabajo no se borran.

---

## Resumen para el administrador

Antes de enviar las instrucciones a tu equipo, necesitas:

1. **Crear el repositorio central** de modelos BP (ejecuta `scripts/setup_repo.sh` o `setup_repo.ps1`)
2. **Subir sistema-b a GitHub** (repo privado de tu organizacion)
3. **Cambiar `antoniarco`** en los comandos de instalacion rapida por tu org/usuario real
4. **Crear el webhook de Slack** y anotar la URL
5. **Enviar a tu equipo** el comando de instalacion (una linea) junto con:
   - La URL del repositorio de modelos BP
   - La URL del webhook de Slack
   - El canal de Slack

Eso es todo. Cada usuario pega el comando, responde las preguntas, y esta listo.

# Sistema B — Guia de configuracion y alta de usuarios

## Como funciona

Cada usuario tiene su propio archivo de configuracion en su equipo:

| Sistema  | Ruta del archivo                          |
|----------|-------------------------------------------|
| macOS    | `~/.config/bp/config.toml`                |
| Linux    | `~/.config/bp/config.toml` (o `$XDG_CONFIG_HOME/bp/config.toml`) |
| Windows  | `%APPDATA%\bp\config.toml`                |

> **No existe un servidor central de usuarios.** Cada persona configura su equipo
> con su nombre y el acceso al repositorio. El repositorio Git central es el unico
> recurso compartido.

---

## Dar de alta un nuevo usuario

### Paso 1: Instalar Sistema B en su equipo

```bash
# Opcion A: con pip (requiere Python 3.11+)
pip install sistema-b

# Opcion B: con pipx (recomendado, aislado)
pipx install sistema-b
```

### Paso 2: Ejecutar el asistente de configuracion

```bash
bp setup
```

El asistente pide:
1. Nombre completo
2. Email
3. Rol (`user` o `admin`)
4. URL del repositorio central
5. Carpeta de trabajo local
6. Webhook de Slack (opcional)
7. Configuracion de bloqueos

### Paso 3 (alternativa): Crear el archivo manualmente

Si prefieres preparar el archivo de antemano y enviarselo al usuario,
copia esta plantilla y rellena los campos:

```toml
# ─────────────────────────────────────────────────────────
# Configuracion de Sistema B
# Archivo: ~/.config/bp/config.toml
# ─────────────────────────────────────────────────────────

[user]
nombre = "NOMBRE COMPLETO DEL USUARIO"    # Ej: "Maria Lopez"
email  = "EMAIL DEL USUARIO"              # Ej: "maria.lopez@empresa.com"
rol    = "user"                           # "user" o "admin" (ver roles abajo)

[repositorio]
url       = "URL DEL REPOSITORIO CENTRAL" # Ej: "git@github.com:empresa/bp-modelos.git"
workspace = "RUTA LOCAL DE TRABAJO"        # Ej: "~/bp-workspace" o "C:\bp-workspace"

[slack]
webhook_url = "URL DEL WEBHOOK"            # La misma para todos los usuarios
canal       = "#finance-bp-control"        # Canal donde llegan los avisos
activado    = true                         # true o false

[bloqueo]
expiracion_horas       = 24               # Horas antes de que expire una reserva
auto_liberar_tras_push = true             # Liberar reserva al subir cambios
```

### Paso 4: Primera descarga

```bash
bp get
```

Esto clona el repositorio y deja los modelos listos para trabajar.

---

## Roles disponibles

| Rol     | Puede hacer                                                    |
|---------|----------------------------------------------------------------|
| `user`  | get, status, lock, unlock (propio), push, history              |
| `admin` | Todo lo anterior + force-unlock, revert, ver logs de auditoria |

---

## Ejemplos de configuracion por tipo de usuario

### Analista financiero (usuario normal)

```toml
[user]
nombre = "Carlos Garcia"
email  = "carlos.garcia@empresa.com"
rol    = "user"

[repositorio]
url       = "git@github.com:empresa/bp-modelos.git"
workspace = "~/bp-workspace"

[slack]
webhook_url = "https://hooks.slack.com/services/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"
canal       = "#finance-bp-control"
activado    = true

[bloqueo]
expiracion_horas       = 24
auto_liberar_tras_push = true
```

### Responsable de finanzas (admin)

```toml
[user]
nombre = "Ana Martinez"
email  = "ana.martinez@empresa.com"
rol    = "admin"

[repositorio]
url       = "git@github.com:empresa/bp-modelos.git"
workspace = "~/bp-workspace"

[slack]
webhook_url = "https://hooks.slack.com/services/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"
canal       = "#finance-bp-control"
activado    = true

[bloqueo]
expiracion_horas       = 48
auto_liberar_tras_push = false
```

### Usuario en Windows

```toml
[user]
nombre = "Pedro Ruiz"
email  = "pedro.ruiz@empresa.com"
rol    = "user"

[repositorio]
url       = "git@github.com:empresa/bp-modelos.git"
workspace = "C:\\bp-workspace"

[slack]
webhook_url = "https://hooks.slack.com/services/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"
canal       = "#finance-bp-control"
activado    = true

[bloqueo]
expiracion_horas       = 24
auto_liberar_tras_push = true
```

---

## Checklist para dar de alta un usuario

- [ ] El usuario tiene **Python 3.11+** y **Git** instalados
- [ ] El usuario tiene **acceso SSH o HTTPS** al repositorio central
- [ ] Se ha instalado `sistema-b` en su equipo
- [ ] Se ha creado `config.toml` (via `bp setup` o manualmente)
- [ ] Se ha ejecutado `bp get` con exito
- [ ] El usuario ha probado el flujo: `bp lock` → editar → `bp push`
- [ ] (Opcional) Se ha verificado que las notificaciones llegan a Slack

---

## Dar de baja un usuario

1. El usuario puede simplemente dejar de usar la herramienta
2. Si tiene un modelo reservado, un admin ejecuta:
   ```bash
   bp force-unlock MODELO.xlsx
   ```
3. Si se quiere revocar el acceso al repositorio, hacerlo desde GitHub/GitLab
4. No hay que modificar nada en el repositorio central

---

## Campos de configuracion — referencia completa

| Seccion       | Campo                    | Tipo    | Obligatorio | Descripcion                                    |
|---------------|--------------------------|---------|-------------|------------------------------------------------|
| `[user]`      | `nombre`                 | texto   | Si          | Nombre que aparece en locks, historial y Slack  |
| `[user]`      | `email`                  | texto   | Si          | Email del usuario                               |
| `[user]`      | `rol`                    | texto   | Si          | `"user"` o `"admin"`                            |
| `[repositorio]` | `url`                  | texto   | Si          | URL del repo (SSH o HTTPS o ruta local)         |
| `[repositorio]` | `workspace`            | texto   | Si          | Carpeta local donde se descargan los modelos    |
| `[slack]`     | `webhook_url`            | texto   | No          | URL del webhook de Slack                        |
| `[slack]`     | `canal`                  | texto   | No          | Nombre del canal (solo informativo)             |
| `[slack]`     | `activado`               | bool    | No          | `true` / `false`                                |
| `[bloqueo]`   | `expiracion_horas`       | entero  | No          | Horas hasta que expira una reserva (default: 24)|
| `[bloqueo]`   | `auto_liberar_tras_push` | bool    | No          | Liberar reserva automaticamente tras push       |

---

## Valores compartidos entre usuarios

Estos valores deben ser **iguales** para todos los usuarios del mismo equipo:

| Campo               | Por que                                              |
|---------------------|------------------------------------------------------|
| `repositorio.url`   | Todos deben apuntar al mismo repositorio central      |
| `slack.webhook_url` | Las notificaciones deben llegar al mismo canal        |
| `slack.canal`       | Mismo canal para todo el equipo                       |

Estos valores son **individuales** por usuario:

| Campo                | Por que                                             |
|----------------------|-----------------------------------------------------|
| `user.nombre`        | Identifica quien hizo cada accion                    |
| `user.email`         | Email personal                                       |
| `user.rol`           | No todos son admin                                   |
| `repositorio.workspace` | Cada usuario elige donde guardar sus archivos     |

"""Mensajes en español para Sistema B. Sin terminologia Git."""

# ── Exito ──────────────────────────────────────────────────────────────────

GET_OK = "Version actualizada correctamente.\n  📄 {model}  ·  version {version}  ·  por {author} el {date}"
GET_UP_TO_DATE = "Ya tienes la ultima version ({version}). Todo al dia."
GET_FIRST_TIME = "Primera descarga completada."
LOCK_ACQUIRED = "Modelo reservado: [bold]{model}[/bold]\n  Nadie mas puede modificarlo hasta que lo liberes."
UNLOCK_OK = "Modelo liberado: [bold]{model}[/bold]\n  Ahora esta disponible para otros."
PUSH_OK = (
    "Cambios subidos correctamente.\n"
    "  📄 {model}  ·  version {version}\n"
    '  💬 "{comment}"'
)
REVERT_OK = (
    "Modelo restaurado: [bold]{model}[/bold]\n"
    "  Se ha vuelto a la version {version} (registrado como version {new_version})."
)
FORCE_UNLOCK_OK = (
    "Reserva forzada liberada: [bold]{model}[/bold]\n"
    "  Estaba reservado por {user}."
)

# ── Info / Estado ──────────────────────────────────────────────────────────

STATUS_FREE = "✅ Libre"
STATUS_LOCKED = "🔒 Reservado por [bold]{user}[/bold] ({since})"
STATUS_LOCKED_EXPIRED = "⏰ Reserva expirada (era de {user})"
STATUS_LOCAL_MODIFIED = "✏️  Con cambios locales"
STATUS_LOCAL_SYNCED = "✅ Al dia"
STATUS_LOCAL_OUTDATED = "⬇️  Desactualizado"
STATUS_LOCAL_NOT_DOWNLOADED = "📥 Sin descargar"

WHO_LOCKED = (
    "🔒 [bold]{model}[/bold] esta reservado:\n"
    "  👤 Por:    {user}\n"
    "  🕐 Desde:  {since} ({hours}h)"
)
WHO_FREE = "✅ [bold]{model}[/bold] esta libre. Nadie lo tiene reservado."

HISTORY_HEADER = "📜 Historial de versiones"
HISTORY_EMPTY = "No hay historial disponible para '{model}'."

LOGS_HEADER = "📋 Registro de acciones administrativas"
LOGS_EMPTY = "No hay acciones administrativas registradas."

# ── Avisos ─────────────────────────────────────────────────────────────────

WARN_LOCAL_CHANGES = (
    "Tienes cambios locales sin subir en [bold]{model}[/bold].\n"
    "  Si actualizas, se creara una copia de seguridad automatica."
)
WARN_OUTDATED = (
    "Tu copia de [bold]{model}[/bold] esta desactualizada.\n"
    "  Ultima version: {remote_version} (por {author}, {date})\n"
    "  Ejecuta [bold]bp get[/bold] para actualizar."
)
WARN_LOCK_EXPIRING = "Tu reserva sobre [bold]{model}[/bold] expira en {hours}h."

# ── Errores ────────────────────────────────────────────────────────────────

ERR_NOT_CONFIGURED = (
    "Sistema B no esta configurado.\n\n"
    "Ejecuta:  bp setup"
)
ERR_NO_WORKSPACE = (
    "No se encontro el espacio de trabajo.\n\n"
    "Ejecuta:  bp get"
)
ERR_LOCK_DENIED = (
    "'{model}' esta reservado por {user} desde {since}.\n\n"
    "Que puedes hacer:\n"
    "  · Espera a que {user} termine\n"
    "  · Contacta con {user}"
)
ERR_LOCK_NOT_OWNED = (
    "No puedes liberar '{model}' porque no lo tienes reservado.\n"
    "Esta reservado por: {user}"
)
ERR_LOCK_NOT_FOUND = "'{model}' no esta reservado. No hay nada que liberar."
ERR_NO_LOCK_FOR_PUSH = (
    "No puedes subir cambios a '{model}' sin reservarlo primero.\n\n"
    "Ejecuta:  bp lock {model}"
)
ERR_PUSH_OUTDATED = (
    "Tu copia de '{model}' esta desactualizada.\n"
    "{author} subio una version nueva el {date}:\n"
    '  "{comment}"\n\n'
    "Ejecuta:  bp get"
)
ERR_PUSH_NO_CHANGES = (
    "No hay cambios que subir.\n"
    "El archivo es identico a la ultima version."
)
ERR_PUSH_EMPTY_COMMENT = (
    "Debes incluir un comentario con tus cambios.\n\n"
    'Ejemplo:  bp push "ajuste escenario conservador"'
)
ERR_NOT_ADMIN = (
    "Esta accion requiere permisos de administrador.\n"
    "Tu rol actual es: usuario"
)
ERR_MODEL_NOT_FOUND = (
    "No se encontro el modelo '{model}'.\n\n"
    "Ejecuta:  bp status  (para ver los modelos disponibles)"
)
ERR_NETWORK = (
    "No se pudo conectar con el repositorio central.\n\n"
    "Verifica tu conexion a internet e intenta de nuevo."
)
ERR_VERSION_NOT_FOUND = "No se encontro la version {version} en el historial."
ERR_RACE_CONDITION = (
    "Demasiada actividad en este momento.\n\n"
    "Espera unos segundos e intenta de nuevo."
)

# ── Slack ──────────────────────────────────────────────────────────────────

SLACK_LOCK = "🔒 {user} ha reservado {model}"
SLACK_UNLOCK = "🔓 {user} ha liberado {model}"
SLACK_PUSH = '📤 {user} ha subido nueva version de {model}: "{comment}"'
SLACK_FORCE_UNLOCK = "⚡ [ADMIN] {admin} ha forzado la liberacion de {model} (reservado por {user})"
SLACK_REVERT = "⏪ {user} ha restaurado {model} a la version {version}"
SLACK_LOCK_EXPIRED = "⏰ La reserva de {user} sobre {model} ha expirado automaticamente"

# ── Confirmaciones ─────────────────────────────────────────────────────────

CONFIRM_GET_OVERWRITE = "Tienes cambios locales. Se creara una copia de seguridad. Continuar?"
CONFIRM_REVERT = "Vas a restaurar '{model}' a la version {version}. Esto creara una nueva version. Continuar?"
CONFIRM_FORCE_UNLOCK = "Vas a forzar la liberacion de '{model}' (reservado por {user}). Continuar?"

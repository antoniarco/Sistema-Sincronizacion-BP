"""Sistema B — Interfaz web local con FastAPI. Cross-platform."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from bp.config.settings import Settings, CONFIG_FILE, get_settings
from bp.core import git_ops, workspace
from bp.core.lock_manager import acquire_lock, release_lock, check_lock, get_all_locks
from bp.core.version_tracker import (
    is_version_current, get_next_version, append_history,
    read_history, get_remote_version_info, VersionEntry,
)
from bp.core.audit import read_audit_log, log_action, AuditEntry
from bp.core.slack import notify_lock, notify_unlock, notify_push, notify_force_unlock
from bp.utils.errors import BPError

WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

app = FastAPI(title="Sistema B", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ── Helpers ───────────────────────────────────────────────────────────────

def _settings() -> Settings:
    return get_settings()


def _user() -> str:
    return _settings().user.nombre


def _ok(message: str, **extra) -> JSONResponse:
    return JSONResponse({"ok": True, "message": message, **extra})


def _err(message: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"ok": False, "message": message}, status_code=status)


# ── Pages ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(request, "settings.html")


# ── API: Status ───────────────────────────────────────────────────────────

@app.get("/api/status")
async def api_status():
    try:
        settings = _settings()
        user = _user()

        if not workspace.is_initialized(settings):
            return JSONResponse({
                "ok": True,
                "initialized": False,
                "user": user,
                "models": [],
            })

        git_ops.fetch(settings.workspace_path)
        models = workspace.get_models(settings)
        locks = {lock.model: lock for lock in get_all_locks(settings)}
        version_current = is_version_current(settings)

        model_list = []
        for model in models:
            name = model.name
            is_modified = workspace.has_local_changes(settings, model)
            lock = locks.get(name)

            if is_modified:
                local_status = "modified"
                local_label = "Con cambios locales"
            elif not version_current:
                local_status = "outdated"
                local_label = "Desactualizado"
            else:
                local_status = "synced"
                local_label = "Al dia"

            lock_info = None
            if lock:
                lock_info = {
                    "user": lock.locked_by,
                    "since": lock.since_str,
                    "hours": lock.hours_held,
                    "is_mine": lock.locked_by == user,
                }

            log = git_ops.get_log(settings.workspace_path, name, limit=1)
            last_change = log[0]["message"][:60] if log else ""
            last_author = log[0]["author"] if log else ""
            last_date = log[0]["date"] if log else ""

            model_list.append({
                "name": name,
                "local_status": local_status,
                "local_label": local_label,
                "lock": lock_info,
                "last_change": last_change,
                "last_author": last_author,
                "last_date": last_date,
            })

        return JSONResponse({
            "ok": True,
            "initialized": True,
            "user": user,
            "version_current": version_current,
            "models": model_list,
        })
    except Exception as e:
        return _err(str(e), 500)


# ── API: Get (download) ──────────────────────────────────────────────────

@app.post("/api/get")
async def api_get():
    try:
        settings = _settings()

        if not workspace.is_initialized(settings):
            if not settings.repositorio.url:
                return _err("Sistema B no esta configurado. Ve a Ajustes.")
            workspace.init_workspace(settings)
            return _ok("Primera descarga completada.")

        models = workspace.get_models(settings)
        for m in models:
            if workspace.has_local_changes(settings, m):
                workspace.create_backup(m)

        new_sha = git_ops.pull(settings.workspace_path)
        workspace.update_state(settings, new_sha)
        return _ok("Modelos actualizados correctamente.")
    except BPError as e:
        return _err(str(e))
    except Exception as e:
        return _err(str(e), 500)


# ── API: Lock ─────────────────────────────────────────────────────────────

@app.post("/api/lock/{model}")
async def api_lock(model: str):
    try:
        settings = _settings()
        user = _user()
        workspace.ensure_initialized(settings)

        model_path = workspace.find_model(settings, model)
        if not model_path:
            return _err(f"No se encontro el modelo '{model}'.")

        name = model_path.name
        acquire_lock(settings, name, user)
        workspace.update_state(settings, git_ops.get_head_sha(settings.workspace_path))
        notify_lock(settings, user, name)
        return _ok(f"Has reservado '{name}'.")
    except BPError as e:
        return _err(str(e))
    except Exception as e:
        return _err(str(e), 500)


# ── API: Unlock ───────────────────────────────────────────────────────────

@app.post("/api/unlock/{model}")
async def api_unlock(model: str):
    try:
        settings = _settings()
        user = _user()
        workspace.ensure_initialized(settings)

        model_path = workspace.find_model(settings, model)
        if not model_path:
            return _err(f"No se encontro el modelo '{model}'.")

        name = model_path.name
        release_lock(settings, name, user)
        workspace.update_state(settings, git_ops.get_head_sha(settings.workspace_path))
        notify_unlock(settings, user, name)
        return _ok(f"Has liberado '{name}'.")
    except BPError as e:
        return _err(str(e))
    except Exception as e:
        return _err(str(e), 500)


# ── API: Push ─────────────────────────────────────────────────────────────

@app.post("/api/push")
async def api_push(request: Request):
    try:
        body = await request.json()
        comment = body.get("comment", "").strip()
        if not comment:
            return _err("Debes incluir un comentario.")

        settings = _settings()
        user = _user()
        workspace.ensure_initialized(settings)

        models = workspace.get_models(settings)
        changed = [m for m in models if workspace.has_local_changes(settings, m)]
        if not changed:
            return _err("No hay cambios que subir.")

        # Verify locks
        for m in changed:
            lock = check_lock(settings, m.name)
            if not lock or lock.locked_by != user:
                return _err(f"No tienes reservado '{m.name}'. Reservalo primero.")

        # Verify version
        if not is_version_current(settings):
            return _err("Tu copia esta desactualizada. Descarga la ultima version primero.")

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        files_to_push = []

        for m in changed:
            rel = str(m.relative_to(settings.workspace_path))
            files_to_push.append(rel)
            version = get_next_version(settings, m.name)
            append_history(settings, VersionEntry(
                version=version, model=m.name, author=user,
                date=now.strftime("%d/%m/%Y %H:%M"),
                comment=comment, action="push",
            ))

        files_to_push.append(".bp-meta/history.jsonl")
        sha = git_ops.commit_and_push(settings.workspace_path, files_to_push, f"{user}: {comment}")

        if not sha:
            return _err("Demasiada actividad. Intenta de nuevo en unos segundos.")

        workspace.update_state(settings, sha)
        names = ", ".join(m.name for m in changed)
        notify_push(settings, user, names, comment)

        # Auto-unlock
        if settings.bloqueo.auto_liberar_tras_push:
            for m in changed:
                try:
                    release_lock(settings, m.name, user)
                except BPError:
                    pass

        workspace.update_state(settings, git_ops.get_head_sha(settings.workspace_path))
        return _ok(f"Cambios subidos correctamente: {names}")
    except BPError as e:
        return _err(str(e))
    except Exception as e:
        return _err(str(e), 500)


# ── API: History ──────────────────────────────────────────────────────────

@app.get("/api/history")
async def api_history(model: str = None):
    try:
        settings = _settings()
        workspace.ensure_initialized(settings)
        entries = read_history(settings, model=model, limit=50)
        return JSONResponse({
            "ok": True,
            "entries": [e.to_dict() for e in entries],
        })
    except BPError as e:
        return _err(str(e))
    except Exception as e:
        return _err(str(e), 500)


# ── API: Force Unlock (admin) ────────────────────────────────────────────

@app.post("/api/force-unlock/{model}")
async def api_force_unlock(model: str):
    try:
        settings = _settings()
        if not settings.is_admin:
            return _err("Necesitas permisos de administrador.")

        admin = _user()
        workspace.ensure_initialized(settings)

        model_path = workspace.find_model(settings, model)
        if not model_path:
            return _err(f"No se encontro el modelo '{model}'.")

        name = model_path.name
        lock = check_lock(settings, name)
        if not lock:
            return _err(f"'{name}' no esta reservado.")

        prev_user = lock.locked_by
        release_lock(settings, name, admin, force=True)
        log_action(settings, AuditEntry(
            action="force-unlock", user=admin, model=name,
            detail=f"Forzado sobre reserva de {prev_user}",
        ))
        notify_force_unlock(settings, admin, prev_user, name)
        return _ok(f"Reserva de '{name}' forzada liberada (era de {prev_user}).")
    except BPError as e:
        return _err(str(e))
    except Exception as e:
        return _err(str(e), 500)


# ── API: Download file ────────────────────────────────────────────────────

@app.get("/api/download/{model}")
async def api_download_file(model: str):
    try:
        settings = _settings()
        model_path = workspace.find_model(settings, model)
        if not model_path:
            return _err(f"No se encontro el modelo '{model}'.")
        return FileResponse(
            path=str(model_path),
            filename=model_path.name,
            media_type="application/octet-stream",
        )
    except Exception as e:
        return _err(str(e), 500)


# ── API: Open file in system app ─────────────────────────────────────────

@app.post("/api/open/{model}")
async def api_open_file(model: str):
    try:
        from bp.utils.platform import open_file
        settings = _settings()
        model_path = workspace.find_model(settings, model)
        if not model_path:
            return _err(f"No se encontro el modelo '{model}'.")

        open_file(model_path)
        return _ok(f"Abriendo '{model_path.name}'...")
    except Exception as e:
        return _err(str(e), 500)


# ── API: Settings ─────────────────────────────────────────────────────────

@app.get("/api/settings")
async def api_get_settings():
    settings = _settings()
    return JSONResponse({
        "ok": True,
        "config_path": str(CONFIG_FILE),
        "user": {
            "nombre": settings.user.nombre,
            "email": settings.user.email,
            "rol": settings.user.rol,
        },
        "repositorio": {
            "url": settings.repositorio.url,
            "workspace": settings.repositorio.workspace,
        },
        "slack": {
            "webhook_url": settings.slack.webhook_url,
            "canal": settings.slack.canal,
            "activado": settings.slack.activado,
        },
        "bloqueo": {
            "expiracion_horas": settings.bloqueo.expiracion_horas,
            "auto_liberar_tras_push": settings.bloqueo.auto_liberar_tras_push,
        },
    })


@app.post("/api/settings")
async def api_save_settings(request: Request):
    try:
        body = await request.json()
        settings = Settings(
            user=body.get("user", {}),
            repositorio=body.get("repositorio", {}),
            slack=body.get("slack", {}),
            bloqueo=body.get("bloqueo", {}),
        )
        settings.save()
        return _ok("Configuracion guardada correctamente.")
    except Exception as e:
        return _err(str(e), 500)


# ── API: Audit logs ──────────────────────────────────────────────────────

@app.get("/api/logs")
async def api_logs():
    try:
        settings = _settings()
        workspace.ensure_initialized(settings)
        entries = read_audit_log(settings)
        return JSONResponse({
            "ok": True,
            "entries": [e.to_dict() for e in entries],
        })
    except BPError as e:
        return _err(str(e))
    except Exception as e:
        return _err(str(e), 500)

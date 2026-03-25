"""bp force-unlock — Fuerza la liberacion de un modelo (admin)."""

from __future__ import annotations

import typer

from bp.config.settings import get_settings
from bp.config.auth import get_current_user, is_admin
from bp.core import workspace
from bp.core.lock_manager import check_lock, release_lock
from bp.core.audit import log_action, AuditEntry
from bp.core.slack import notify_force_unlock
from bp.i18n import es
from bp.utils.display import success, error, confirm, divider, spinner
from bp.utils.errors import BPError


def run(
    modelo: str = typer.Argument(..., help="Nombre del modelo a liberar"),
) -> None:
    """[Admin] Fuerza la liberacion de un modelo reservado por otro usuario."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        admin_user = get_current_user()
        divider()

        if not is_admin():
            error(es.ERR_NOT_ADMIN)
            raise typer.Exit(1)

        model_path = workspace.find_model(settings, modelo)
        if not model_path:
            error(es.ERR_MODEL_NOT_FOUND.format(model=modelo))
            raise typer.Exit(1)

        model_name = model_path.name

        lock = check_lock(settings, model_name)
        if not lock:
            error(es.ERR_LOCK_NOT_FOUND.format(model=model_name))
            raise typer.Exit(1)

        if not confirm(es.CONFIRM_FORCE_UNLOCK.format(model=model_name, user=lock.locked_by)):
            raise typer.Exit(0)

        with spinner(f"Forzando liberacion de '{model_name}'..."):
            release_lock(settings, model_name, admin_user, force=True)

        log_action(settings, AuditEntry(
            action="force-unlock",
            user=admin_user,
            model=model_name,
            detail=f"Forzado sobre reserva de {lock.locked_by}",
        ))

        success(es.FORCE_UNLOCK_OK.format(model=model_name, user=lock.locked_by))
        notify_force_unlock(settings, admin_user, lock.locked_by, model_name)
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

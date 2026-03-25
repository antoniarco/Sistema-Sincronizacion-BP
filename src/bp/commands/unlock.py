"""bp unlock — Libera la reserva de un modelo."""

from __future__ import annotations

import typer

from bp.config.settings import get_settings
from bp.config.auth import get_current_user
from bp.core import git_ops, workspace
from bp.core.lock_manager import release_lock
from bp.core.slack import notify_unlock
from bp.i18n import es
from bp.utils.display import success, error, divider, spinner
from bp.utils.errors import BPError


def run(
    modelo: str = typer.Argument(..., help="Nombre del modelo a liberar (ej: BP_Anual.xlsx)"),
) -> None:
    """Libera la reserva de un modelo para que otros puedan trabajar."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        user = get_current_user()
        divider()

        model_path = workspace.find_model(settings, modelo)
        if not model_path:
            error(es.ERR_MODEL_NOT_FOUND.format(model=modelo))
            raise typer.Exit(1)

        model_name = model_path.name

        with spinner(f"Liberando '{model_name}'..."):
            release_lock(settings, model_name, user)
            workspace.update_state(settings, git_ops.get_head_sha(settings.workspace_path))

        success(es.UNLOCK_OK.format(model=model_name))
        notify_unlock(settings, user, model_name)
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

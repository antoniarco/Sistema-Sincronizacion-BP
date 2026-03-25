"""bp lock — Reserva un modelo para trabajar."""

from __future__ import annotations

import typer

from bp.config.settings import get_settings
from bp.config.auth import get_current_user
from bp.core import git_ops, workspace
from bp.core.lock_manager import acquire_lock
from bp.core.slack import notify_lock
from bp.i18n import es
from bp.utils.display import success, error, hint, divider, spinner
from bp.utils.errors import BPError


def run(
    modelo: str = typer.Argument(..., help="Nombre del modelo a reservar (ej: BP_Anual.xlsx)"),
) -> None:
    """Reserva un modelo para que solo tu puedas modificarlo."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        user = get_current_user()
        divider()

        # Verificar que el modelo existe
        model_path = workspace.find_model(settings, modelo)
        if not model_path:
            error(es.ERR_MODEL_NOT_FOUND.format(model=modelo))
            raise typer.Exit(1)

        model_name = model_path.name

        # Intentar adquirir el lock
        with spinner(f"Reservando '{model_name}'..."):
            lock_info = acquire_lock(settings, model_name, user)
            workspace.update_state(settings, git_ops.get_head_sha(settings.workspace_path))

        success(es.LOCK_ACQUIRED.format(model=model_name))
        notify_lock(settings, user, model_name)

        hint("Edita el archivo y luego ejecuta [bold green]bp push[/bold green] [dim]\"tu comentario\"[/dim]")
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

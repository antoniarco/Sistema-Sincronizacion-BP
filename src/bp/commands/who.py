"""bp who — Muestra quien tiene reservado un modelo."""

from __future__ import annotations

import typer

from bp.config.settings import get_settings
from bp.core import workspace
from bp.core.lock_manager import check_lock
from bp.i18n import es
from bp.utils.display import info, error, divider, spinner
from bp.utils.errors import BPError


def run(
    modelo: str = typer.Argument(..., help="Nombre del modelo a consultar"),
) -> None:
    """Muestra quien tiene reservado un modelo y desde cuando."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        divider()

        model_path = workspace.find_model(settings, modelo)
        if not model_path:
            error(es.ERR_MODEL_NOT_FOUND.format(model=modelo))
            raise typer.Exit(1)

        model_name = model_path.name

        with spinner("Consultando..."):
            lock = check_lock(settings, model_name)

        if lock:
            info(es.WHO_LOCKED.format(
                model=model_name,
                user=lock.locked_by,
                since=lock.since_str,
                hours=lock.hours_held,
            ))
        else:
            info(es.WHO_FREE.format(model=model_name))
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

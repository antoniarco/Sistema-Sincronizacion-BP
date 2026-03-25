"""bp get — Descarga la ultima version del modelo."""

from __future__ import annotations

import typer

from bp.config.settings import get_settings
from bp.config.auth import get_current_user
from bp.core import git_ops, workspace
from bp.core.version_tracker import get_remote_version_info
from bp.i18n import es
from bp.utils.display import success, warning, error, info, hint, divider, spinner, confirm, console
from bp.utils.errors import BPError


def run() -> None:
    """Descarga la ultima version de los modelos."""
    try:
        settings = get_settings()
        divider()

        # Si no hay workspace, inicializar
        if not workspace.is_initialized(settings):
            if not settings.repositorio.url:
                error(es.ERR_NOT_CONFIGURED)
                raise typer.Exit(1)

            info("  📥 Primera descarga — preparando espacio de trabajo...")
            with spinner("Descargando modelos del repositorio central..."):
                workspace.init_workspace(settings)

            success(es.GET_FIRST_TIME)
            _show_downloaded_models(settings)
            hint("Ejecuta [bold green]bp status[/bold green] para ver el estado de tus modelos")
            divider()
            return

        # Comprobar cambios locales antes de actualizar
        models = workspace.get_models(settings)
        models_with_changes = [m for m in models if workspace.has_local_changes(settings, m)]

        if models_with_changes:
            names = ", ".join(m.name for m in models_with_changes)
            warning(es.WARN_LOCAL_CHANGES.format(model=names))
            if not confirm(es.CONFIRM_GET_OVERWRITE):
                raise typer.Exit(0)
            for m in models_with_changes:
                backup = workspace.create_backup(m)
                info(f"  💾 Copia de seguridad: [dim]{backup.name}[/dim]")

        # Actualizar
        with spinner("Descargando ultima version..."):
            new_sha = git_ops.pull(settings.workspace_path)
            workspace.update_state(settings, new_sha)

        # Mostrar resultado
        remote_info = get_remote_version_info(settings)
        if remote_info:
            success(es.GET_OK.format(
                version=remote_info["sha"],
                model="modelos",
                author=remote_info["author"],
                date=remote_info["date"],
            ))
        else:
            success(es.GET_UP_TO_DATE.format(version=new_sha[:8]))

        _show_downloaded_models(settings)
        hint("Ejecuta [bold green]bp lock[/bold green] [dim]modelo[/dim] para reservar y empezar a trabajar")
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)


def _show_downloaded_models(settings) -> None:
    """Muestra los modelos descargados."""
    models = workspace.get_models(settings)
    if models:
        divider()
        info(f"  [bold]Modelos disponibles ({len(models)}):[/bold]")
        for m in models:
            info(f"    📄 {m.name}")

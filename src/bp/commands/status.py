"""bp status — Muestra el estado de los modelos."""

from __future__ import annotations

import typer

from bp.config.settings import get_settings
from bp.core import git_ops, workspace
from bp.core.lock_manager import get_all_locks
from bp.core.version_tracker import is_version_current
from bp.i18n import es
from bp.utils.display import console, create_table, warning, error, info, hint, divider, spinner
from bp.utils.errors import BPError


def run() -> None:
    """Muestra el estado de todos los modelos."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        divider()

        # Fetch para tener info actualizada
        with spinner("Consultando estado..."):
            git_ops.fetch(settings.workspace_path)

        models = workspace.get_models(settings)
        if not models:
            info("  No hay modelos en el espacio de trabajo.")
            hint("Ejecuta [bold green]bp get[/bold green] para descargar los modelos")
            divider()
            return

        # Obtener todos los locks activos
        locks = {lock.model: lock for lock in get_all_locks(settings)}

        # Comprobar si estamos al dia
        version_current = is_version_current(settings)

        # Header con info del usuario
        user = settings.user.nombre
        info(f"  [bold]👤 {user}[/bold]  ·  [dim]{settings.repositorio.workspace}[/dim]")
        divider()

        table = create_table(
            "Estado de tus modelos",
            [
                ("", ""),
                ("Modelo", "bold"),
                ("Tu copia", ""),
                ("Reserva", ""),
                ("Ultimo cambio", "dim"),
            ],
        )

        has_changes = False
        has_locks_by_me = False

        for model in models:
            model_name = model.name

            # Estado local
            is_modified = workspace.has_local_changes(settings, model)
            if is_modified:
                local_status = f"[bold yellow]{es.STATUS_LOCAL_MODIFIED}[/bold yellow]"
                has_changes = True
            elif not version_current:
                local_status = f"[bold red]{es.STATUS_LOCAL_OUTDATED}[/bold red]"
            else:
                local_status = f"[green]{es.STATUS_LOCAL_SYNCED}[/green]"

            # Estado de reserva
            lock = locks.get(model_name)
            is_locked = lock is not None
            if lock:
                if lock.locked_by == user:
                    lock_status = f"[bold cyan]🔒 Reservado por ti ({lock.hours_held}h)[/bold cyan]"
                    has_locks_by_me = True
                else:
                    lock_status = f"[yellow]🔒 {lock.locked_by} ({lock.hours_held}h)[/yellow]"
            else:
                lock_status = f"[green]{es.STATUS_FREE}[/green]"

            # Icono
            if is_locked and lock and lock.locked_by == user and is_modified:
                icon = "📝"  # editando
            elif is_locked:
                icon = "🔒"
            elif is_modified:
                icon = "✏️"
            elif not version_current:
                icon = "⬇️"
            else:
                icon = "✅"

            # Ultimo cambio
            log = git_ops.get_log(settings.workspace_path, model_name, limit=1)
            last_change = log[0]["message"][:40] if log else "-"

            table.add_row(icon, model_name, local_status, lock_status, last_change)

        console.print(table)

        # Sugerencias contextuales
        if not version_current and not has_changes:
            divider()
            warning("Tu copia esta desactualizada.")
            hint("Ejecuta [bold green]bp get[/bold green] para actualizar")
        elif has_changes and has_locks_by_me:
            divider()
            hint('Ejecuta [bold green]bp push[/bold green] [dim]"tu comentario"[/dim] para subir tus cambios')
        elif has_changes and not has_locks_by_me:
            divider()
            hint("Ejecuta [bold green]bp lock[/bold green] [dim]modelo[/dim] antes de subir tus cambios")
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

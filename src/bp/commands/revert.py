"""bp revert — Restaura una version anterior."""

from __future__ import annotations

from datetime import datetime, timezone

import typer

from bp.config.settings import get_settings
from bp.config.auth import get_current_user, is_admin
from bp.core import git_ops, workspace
from bp.core.version_tracker import (
    get_version_by_number, get_next_version, append_history, VersionEntry,
)
from bp.core.audit import log_action, AuditEntry
from bp.core.slack import notify_revert
from bp.i18n import es
from bp.utils.display import success, error, confirm
from bp.utils.errors import BPError


def run(
    version: int = typer.Argument(..., help="Numero de version a restaurar (ej: 3)"),
    modelo: str = typer.Argument(..., help="Nombre del modelo"),
) -> None:
    """Restaura una version anterior de un modelo. Crea una nueva version en el historial."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        user = get_current_user()

        # Solo admin o supervisor puede revertir
        if not is_admin():
            error(es.ERR_NOT_ADMIN)
            raise typer.Exit(1)

        # Buscar la version en el historial
        entry = get_version_by_number(settings, modelo, version)
        if not entry:
            error(es.ERR_VERSION_NOT_FOUND.format(version=version))
            raise typer.Exit(1)

        # Confirmar
        if not confirm(es.CONFIRM_REVERT.format(model=modelo, version=version)):
            raise typer.Exit(0)

        # Obtener contenido del archivo en esa version
        file_content = git_ops.get_file_at_version(
            settings.workspace_path, modelo, entry.sha
        )

        if file_content is None:
            # Fallback: intentar obtener del historial git directamente
            error(es.ERR_VERSION_NOT_FOUND.format(version=version))
            raise typer.Exit(1)

        # Escribir el archivo restaurado
        model_path = workspace.find_model(settings, modelo)
        if not model_path:
            error(es.ERR_MODEL_NOT_FOUND.format(model=modelo))
            raise typer.Exit(1)

        model_path.write_bytes(file_content)

        # Registrar en historial como nueva version
        new_version = get_next_version(settings, modelo)
        now = datetime.now(timezone.utc)
        history_entry = VersionEntry(
            version=new_version,
            model=modelo,
            author=user,
            date=now.strftime("%d/%m/%Y %H:%M"),
            comment=f"Restauracion a version {version}",
            action="revert",
        )
        append_history(settings, history_entry)

        # Commit y push
        rel_path = str(model_path.relative_to(settings.workspace_path))
        sha = git_ops.commit_and_push(
            settings.workspace_path,
            [rel_path, ".bp-meta/history.jsonl"],
            f"revert: {user} restaura {modelo} a v{version}",
        )

        if sha:
            workspace.update_state(settings, sha)

        # Auditar
        log_action(settings, AuditEntry(
            action="revert",
            user=user,
            model=modelo,
            detail=f"Restaurado a version {version}",
        ))

        success(es.REVERT_OK.format(
            model=modelo,
            version=version,
            new_version=new_version,
        ))

        notify_revert(settings, user, modelo, version)

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

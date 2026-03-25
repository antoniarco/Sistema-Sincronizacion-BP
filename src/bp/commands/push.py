"""bp push — Sube cambios con comentario."""

from __future__ import annotations

from datetime import datetime, timezone

import typer

from bp.config.settings import get_settings
from bp.config.auth import get_current_user
from bp.core import git_ops, workspace
from bp.core.lock_manager import check_lock, release_lock
from bp.core.version_tracker import (
    is_version_current, get_next_version, append_history,
    get_remote_version_info, VersionEntry,
)
from bp.core.slack import notify_push
from bp.i18n import es
from bp.utils.display import success, error, info, hint, divider, spinner
from bp.utils.errors import BPError


def run(
    comentario: str = typer.Argument(..., help='Comentario sobre los cambios (ej: "ajuste escenario base")'),
) -> None:
    """Sube tus cambios al repositorio central con un comentario descriptivo."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        user = get_current_user()
        divider()

        # Validar comentario
        if not comentario or not comentario.strip():
            error(es.ERR_PUSH_EMPTY_COMMENT)
            raise typer.Exit(1)

        # Buscar modelos con cambios
        models = workspace.get_models(settings)
        changed_models = [m for m in models if workspace.has_local_changes(settings, m)]

        if not changed_models:
            error(es.ERR_PUSH_NO_CHANGES.format(model="tus modelos"))
            raise typer.Exit(1)

        info(f"  📤 Subiendo cambios en {len(changed_models)} modelo(s)...")
        divider()

        # Verificar locks y version para cada modelo modificado
        for model_path in changed_models:
            model_name = model_path.name

            lock = check_lock(settings, model_name)
            if not lock or lock.locked_by != user:
                error(es.ERR_NO_LOCK_FOR_PUSH.format(model=model_name))
                raise typer.Exit(1)

        # Verificar version actualizada
        if not is_version_current(settings):
            remote_info = get_remote_version_info(settings)
            if remote_info:
                error(es.ERR_PUSH_OUTDATED.format(
                    model=changed_models[0].name,
                    author=remote_info["author"],
                    date=remote_info["date"],
                    comment=remote_info["message"][:60],
                ))
            else:
                error(es.ERR_PUSH_OUTDATED.format(
                    model=changed_models[0].name,
                    author="desconocido", date="", comment="",
                ))
            raise typer.Exit(1)

        # Preparar archivos para commit
        files_to_push = []
        for model_path in changed_models:
            rel_path = str(model_path.relative_to(settings.workspace_path))
            files_to_push.append(rel_path)

        # Registrar en historial
        now = datetime.now(timezone.utc)
        for model_path in changed_models:
            version = get_next_version(settings, model_path.name)
            entry = VersionEntry(
                version=version,
                model=model_path.name,
                author=user,
                date=now.strftime("%d/%m/%Y %H:%M"),
                comment=comentario.strip(),
                action="push",
            )
            append_history(settings, entry)

        files_to_push.append(".bp-meta/history.jsonl")

        # Commit y push
        with spinner("Subiendo cambios al repositorio central..."):
            sha = git_ops.commit_and_push(
                settings.workspace_path,
                files_to_push,
                f"{user}: {comentario.strip()}",
            )

        if not sha:
            error(es.ERR_RACE_CONDITION)
            raise typer.Exit(1)

        workspace.update_state(settings, sha)

        # Mostrar exito
        for model_path in changed_models:
            version = get_next_version(settings, model_path.name) - 1
            success(es.PUSH_OK.format(
                model=model_path.name,
                version=f"v{version}",
                comment=comentario.strip(),
            ))

        # Notificar Slack
        model_names = ", ".join(m.name for m in changed_models)
        notify_push(settings, user, model_names, comentario.strip())

        # Auto-liberar locks
        if settings.bloqueo.auto_liberar_tras_push:
            for model_path in changed_models:
                try:
                    release_lock(settings, model_path.name, user)
                    info(f"  🔓 Reserva de '{model_path.name}' liberada automaticamente.")
                except BPError:
                    pass

        workspace.update_state(settings, git_ops.get_head_sha(settings.workspace_path))

        hint("Ejecuta [bold green]bp status[/bold green] para verificar el estado")
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

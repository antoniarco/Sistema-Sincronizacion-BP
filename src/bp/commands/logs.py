"""bp logs — Muestra el registro de acciones administrativas."""

from __future__ import annotations

import typer

from bp.config.settings import get_settings
from bp.core import workspace
from bp.core.audit import read_audit_log
from bp.i18n import es
from bp.utils.display import console, create_table, info, error, divider
from bp.utils.errors import BPError


def run() -> None:
    """Muestra el registro de acciones administrativas (force-unlock, revert, etc.)."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        divider()

        entries = read_audit_log(settings)

        if not entries:
            info(f"  {es.LOGS_EMPTY}")
            divider()
            return

        table = create_table(
            es.LOGS_HEADER,
            [
                ("", ""),
                ("Fecha", "dim"),
                ("Accion", "bold"),
                ("Usuario", ""),
                ("Modelo", ""),
                ("Detalle", ""),
            ],
        )

        for entry in entries:
            icon = "⚡" if "force" in entry.action else "⏪"
            table.add_row(
                icon,
                entry.date_str,
                entry.action,
                entry.user,
                entry.model,
                entry.detail,
            )

        console.print(table)
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

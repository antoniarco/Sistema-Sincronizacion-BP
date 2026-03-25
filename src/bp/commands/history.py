"""bp history — Muestra el historial de versiones."""

from __future__ import annotations

from typing import Optional

import typer

from bp.config.settings import get_settings
from bp.core import workspace
from bp.core.version_tracker import read_history
from bp.i18n import es
from bp.utils.display import console, create_table, info, error, divider
from bp.utils.errors import BPError


def run(
    modelo: Optional[str] = typer.Argument(None, help="Modelo especifico (opcional)"),
    todas: bool = typer.Option(False, "--todas", help="Mostrar todo el historial"),
) -> None:
    """Muestra el historial de versiones de los modelos."""
    try:
        settings = get_settings()
        workspace.ensure_initialized(settings)
        divider()

        limit = 1000 if todas else 20
        entries = read_history(settings, model=modelo, limit=limit)

        if not entries:
            info(f"  {es.HISTORY_EMPTY.format(model=modelo or 'los modelos')}")
            divider()
            return

        table = create_table(
            es.HISTORY_HEADER,
            [
                ("", ""),
                ("Version", "bold cyan"),
                ("Modelo", ""),
                ("Autor", "bold"),
                ("Fecha", "dim"),
                ("Comentario", ""),
            ],
        )

        for entry in entries:
            if entry.action == "revert":
                icon = "⏪"
            else:
                icon = "📤"

            table.add_row(
                icon,
                f"v{entry.version}",
                entry.model,
                entry.author,
                entry.date,
                entry.comment,
            )

        console.print(table)
        divider()

    except BPError as e:
        error(str(e))
        raise typer.Exit(1)

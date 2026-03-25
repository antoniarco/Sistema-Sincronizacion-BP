"""Punto de entrada principal del CLI de Sistema B."""

from __future__ import annotations

import typer

from bp.commands import get, status, lock, unlock, push, history, revert, force_unlock, who, logs, setup, web

app = typer.Typer(
    name="bp",
    help="Sistema B — Gestiona tus modelos BP de forma simple y segura.",
    invoke_without_command=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
    add_completion=False,
)


@app.callback()
def main(ctx: typer.Context) -> None:
    """Sistema B — Gestiona tus modelos BP de forma simple y segura."""
    if ctx.invoked_subcommand is None:
        _show_dashboard()


def _show_dashboard() -> None:
    """Muestra el panel de bienvenida con estado y comandos."""
    from bp.config.settings import get_settings, CONFIG_FILE
    from bp.utils.display import (
        show_welcome, show_workflow_guide, show_commands_help,
        console, info, warning,
    )

    settings = get_settings()

    # Si no esta configurado, mostrar guia de inicio
    if not settings.user.nombre:
        console.print()
        console.print(
            "[bold cyan]  Sistema B[/bold cyan]  [dim]v0.1.0[/dim]\n"
            "  Control de versiones para modelos BP\n"
        )
        warning("No tienes Sistema B configurado todavia.")
        info("")
        info("  Para empezar, ejecuta:  [bold green]bp setup[/bold green]")
        console.print()
        return

    # Dashboard principal
    show_welcome(settings.user.nombre, settings.repositorio.workspace)
    console.print()
    show_workflow_guide()
    console.print()
    show_commands_help()


# ── Comandos diarios ─────────────────────────────────────────────────────

app.command(
    "web",
    help="🌐  Abre la interfaz visual en el navegador.",
    rich_help_panel="Configuracion",
)(web.run)

app.command(
    "setup",
    help="⚙️  Configura Sistema B en tu equipo.",
    rich_help_panel="Configuracion",
)(setup.run)

app.command(
    "get",
    help="📥  Descarga la ultima version de los modelos.",
    rich_help_panel="Dia a dia",
)(get.run)

app.command(
    "status",
    help="📊  Muestra el estado de tus modelos.",
    rich_help_panel="Dia a dia",
)(status.run)

app.command(
    "lock",
    help="🔒  Reserva un modelo para trabajar.",
    rich_help_panel="Dia a dia",
)(lock.run)

app.command(
    "unlock",
    help="🔓  Libera la reserva de un modelo.",
    rich_help_panel="Dia a dia",
)(unlock.run)

app.command(
    "push",
    help="📤  Sube tus cambios con un comentario.",
    rich_help_panel="Dia a dia",
)(push.run)

app.command(
    "who",
    help="👤  Muestra quien tiene reservado un modelo.",
    rich_help_panel="Dia a dia",
)(who.run)

app.command(
    "history",
    help="📜  Muestra el historial de versiones.",
    rich_help_panel="Dia a dia",
)(history.run)

# ── Comandos admin ───────────────────────────────────────────────────────

app.command(
    "force-unlock",
    help="⚡  [Admin] Fuerza la liberacion de un modelo.",
    rich_help_panel="Administracion",
)(force_unlock.run)

app.command(
    "revert",
    help="⏪  [Admin] Restaura una version anterior.",
    rich_help_panel="Administracion",
)(revert.run)

app.command(
    "logs",
    help="📋  [Admin] Registro de acciones administrativas.",
    rich_help_panel="Administracion",
)(logs.run)

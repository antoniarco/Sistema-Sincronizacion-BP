"""Helpers de visualizacion con Rich — UX amigable para usuarios no tecnicos."""

from __future__ import annotations

from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

console = Console()
error_console = Console(stderr=True)


# ── Mensajes basicos ──────────────────────────────────────────────────────

def success(msg: str) -> None:
    console.print(f"  [bold green]✅  {msg}[/bold green]")


def warning(msg: str) -> None:
    console.print(f"  [bold yellow]⚠️   {msg}[/bold yellow]")


def error(msg: str) -> None:
    error_console.print()
    error_console.print(Panel(
        f"[bold red]{msg}[/bold red]",
        title="[red]Error[/red]",
        border_style="red",
        padding=(1, 2),
    ))


def info(msg: str) -> None:
    console.print(f"  {msg}")


def hint(msg: str) -> None:
    """Muestra una sugerencia de siguiente paso."""
    console.print(f"\n  [dim]💡 Siguiente paso:[/dim] [bold]{msg}[/bold]")


def divider() -> None:
    console.print()


# ── Spinner para operaciones de red ───────────────────────────────────────

@contextmanager
def spinner(msg: str):
    """Muestra un spinner mientras se ejecuta una operacion."""
    with console.status(f"  [cyan]{msg}[/cyan]", spinner="dots"):
        yield


# ── Tablas ────────────────────────────────────────────────────────────────

def create_table(title: str, columns: list[tuple[str, str]]) -> Table:
    """Crea una tabla Rich con las columnas dadas como (nombre, estilo)."""
    table = Table(
        title=f"  {title}",
        show_header=True,
        header_style="bold white on dark_blue",
        border_style="blue",
        title_style="bold cyan",
        padding=(0, 1),
        show_lines=True,
    )
    for name, style in columns:
        table.add_column(name, style=style)
    return table


# ── Confirmacion ──────────────────────────────────────────────────────────

def confirm(msg: str) -> bool:
    """Pide confirmacion al usuario."""
    from rich.prompt import Confirm
    return Confirm.ask(f"  [yellow]⚠️  {msg}[/yellow]")


# ── Panel de bienvenida ──────────────────────────────────────────────────

def show_welcome(user: str, workspace: str) -> None:
    """Muestra el panel de bienvenida con el flujo de trabajo."""
    console.print()
    console.print(Panel(
        f"[bold cyan]Sistema B[/bold cyan]  [dim]v0.1.0[/dim]\n"
        f"Control de versiones para modelos BP\n\n"
        f"[bold]👤 Usuario:[/bold]  {user}\n"
        f"[bold]📁 Espacio:[/bold]  {workspace}",
        border_style="cyan",
        padding=(1, 2),
    ))


def show_workflow_guide() -> None:
    """Muestra la guia visual del flujo de trabajo."""
    flow = (
        "[bold white on dark_blue]  FLUJO DE TRABAJO  [/bold white on dark_blue]\n\n"
        "  [bold cyan]1.[/bold cyan]  [bold]bp get[/bold]              📥  Descarga la ultima version\n"
        "  [bold cyan]2.[/bold cyan]  [bold]bp lock[/bold] modelo      🔒  Reserva el modelo\n"
        "  [bold cyan]3.[/bold cyan]  [dim]Edita el archivo en Excel/herramienta[/dim]\n"
        "  [bold cyan]4.[/bold cyan]  [bold]bp push[/bold] \"comentario\" 📤  Sube tus cambios\n\n"
        "  [dim]La reserva se libera automaticamente al subir.[/dim]"
    )
    console.print(Panel(flow, border_style="blue", padding=(1, 2)))


def show_commands_help() -> None:
    """Muestra los comandos agrupados por categoria."""
    # Comandos diarios
    daily = Table(
        title="📋 Comandos del dia a dia",
        show_header=True,
        header_style="bold white on dark_blue",
        border_style="blue",
        padding=(0, 1),
        title_style="bold cyan",
    )
    daily.add_column("Comando", style="bold green", min_width=28)
    daily.add_column("Descripcion", style="")
    daily.add_row("bp get",                  "📥  Descarga la ultima version")
    daily.add_row("bp status",               "📊  Ve el estado de tus modelos")
    daily.add_row("bp lock [dim]modelo[/dim]",   "🔒  Reserva un modelo para editar")
    daily.add_row("bp unlock [dim]modelo[/dim]", "🔓  Libera la reserva de un modelo")
    daily.add_row('bp push [dim]"comentario"[/dim]', "📤  Sube tus cambios")
    daily.add_row("bp who [dim]modelo[/dim]",    "👤  Mira quien tiene reservado un modelo")
    daily.add_row("bp history",              "📜  Consulta el historial de versiones")

    console.print(daily)
    console.print()

    # Comandos admin
    admin = Table(
        title="🔧 Comandos de administracion",
        show_header=True,
        header_style="bold white on red",
        border_style="red",
        padding=(0, 1),
        title_style="bold red",
    )
    admin.add_column("Comando", style="bold yellow", min_width=28)
    admin.add_column("Descripcion", style="")
    admin.add_row("bp force-unlock [dim]modelo[/dim]", "⚡  Fuerza la liberacion de una reserva")
    admin.add_row("bp revert [dim]version modelo[/dim]", "⏪  Restaura una version anterior")
    admin.add_row("bp logs",                 "📋  Ve el registro de acciones admin")

    console.print(admin)
    console.print()

    # Setup
    console.print("  [dim]Configuracion:[/dim]  [bold]bp setup[/bold]  — Configura Sistema B en tu equipo")
    console.print()


# ── Panel de estado del modelo ────────────────────────────────────────────

def model_status_icon(local_status: str, is_locked: bool) -> str:
    """Devuelve un icono representativo del estado."""
    if is_locked:
        return "🔒"
    if "cambios" in local_status.lower() or "modif" in local_status.lower():
        return "✏️"
    if "desactualizado" in local_status.lower():
        return "⬇️"
    return "✅"

"""bp setup — Configura Sistema B de forma interactiva."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from bp.config.settings import Settings, CONFIG_FILE, CONFIG_DIR
from bp.utils.display import success, warning, error, info
from bp.utils.platform import platform_name, run_command

console = Console()


def run() -> None:
    """Configura Sistema B paso a paso. Funciona en macOS, Linux y Windows."""
    console.print()
    console.print(Panel(
        "[bold cyan]Sistema B[/bold cyan] — Configuracion inicial\n\n"
        "Este asistente te guiara para configurar tu entorno.\n"
        "Solo necesitas hacerlo una vez.",
        title="Bienvenido",
        border_style="cyan",
    ))
    console.print()

    info(f"  Sistema detectado: {platform_name()}")

    # Cargar config existente si hay
    existing = Settings.load()
    has_existing = CONFIG_FILE.exists()

    if has_existing:
        warning(f"Ya existe una configuracion en: {CONFIG_FILE}")
        overwrite = Prompt.ask(
            "Quieres modificarla?",
            choices=["si", "no"],
            default="si",
        )
        if overwrite == "no":
            info("Configuracion sin cambios.")
            return

    # 1. Datos del usuario
    console.print("\n[bold]1. Tus datos[/bold]")
    nombre = Prompt.ask(
        "  Tu nombre completo",
        default=existing.user.nombre or _detect_git_user(),
    )
    email = Prompt.ask(
        "  Tu email",
        default=existing.user.email or _detect_git_email(),
    )
    rol = Prompt.ask(
        "  Tu rol",
        choices=["user", "admin"],
        default=existing.user.rol,
    )

    # 2. Repositorio
    console.print("\n[bold]2. Repositorio central[/bold]")
    info("  Puede ser una ruta local o remota (git@github.com:org/repo.git)")
    repo_url = Prompt.ask(
        "  URL del repositorio",
        default=existing.repositorio.url or "",
    )

    default_workspace = existing.repositorio.workspace or str(Path.home() / "bp-workspace")
    workspace = Prompt.ask(
        "  Carpeta de trabajo local",
        default=default_workspace,
    )

    # 3. Slack
    console.print("\n[bold]3. Notificaciones por Slack[/bold] (opcional)")
    slack_url = Prompt.ask(
        "  Webhook URL de Slack (dejar vacio para omitir)",
        default=existing.slack.webhook_url or "",
    )
    slack_activo = bool(slack_url.strip())
    canal = existing.slack.canal
    if slack_activo:
        canal = Prompt.ask("  Canal de Slack", default=existing.slack.canal)

    # 4. Bloqueo
    console.print("\n[bold]4. Configuracion de bloqueos[/bold]")
    expiracion = Prompt.ask(
        "  Horas antes de que expire una reserva",
        default=str(existing.bloqueo.expiracion_horas),
    )
    auto_liberar = Prompt.ask(
        "  Liberar reserva automaticamente tras subir cambios?",
        choices=["si", "no"],
        default="si" if existing.bloqueo.auto_liberar_tras_push else "no",
    )

    # Construir y guardar
    settings = Settings(
        user={"nombre": nombre, "email": email, "rol": rol},
        repositorio={"url": repo_url, "workspace": workspace},
        slack={"webhook_url": slack_url, "canal": canal, "activado": slack_activo},
        bloqueo={"expiracion_horas": int(expiracion), "auto_liberar_tras_push": auto_liberar == "si"},
    )
    settings.save()

    console.print()
    success(f"Configuracion guardada en: {CONFIG_FILE}")

    if repo_url:
        console.print()
        _verify_repo(repo_url)

    console.print()
    console.print(Panel(
        f"[bold]Usuario:[/bold]     {nombre} ({rol})\n"
        f"[bold]Email:[/bold]       {email}\n"
        f"[bold]Repositorio:[/bold] {repo_url}\n"
        f"[bold]Workspace:[/bold]   {workspace}\n"
        f"[bold]Slack:[/bold]       {'Activado' if slack_activo else 'Desactivado'}\n"
        f"[bold]Expiracion:[/bold]  {expiracion}h",
        title="Resumen",
        border_style="green",
    ))

    console.print()
    info("Siguiente paso: ejecuta [bold]bp get[/bold] para descargar los modelos.")


def _detect_git_user() -> str:
    try:
        result = run_command(["git", "config", "--global", "user.name"])
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def _detect_git_email() -> str:
    try:
        result = run_command(["git", "config", "--global", "user.email"])
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def _verify_repo(url: str) -> None:
    try:
        result = run_command(["git", "ls-remote", "--exit-code", url], timeout=15)
        if result.returncode == 0:
            success("Conexion con el repositorio: OK")
        else:
            warning("No se pudo verificar el repositorio. Comprueba la URL y tus permisos.")
    except Exception:
        warning("No se pudo verificar el repositorio.")

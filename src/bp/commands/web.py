"""bp web — Abre la interfaz web de Sistema B."""

from __future__ import annotations

import threading
import time

import typer

from bp.utils.display import success, info, divider, console
from bp.utils.platform import open_url


def run(
    port: int = typer.Option(8000, "--port", "-p", help="Puerto del servidor (default: 8000)"),
    no_browser: bool = typer.Option(False, "--no-browser", help="No abrir el navegador automaticamente"),
) -> None:
    """Abre la interfaz web de Sistema B en tu navegador."""
    divider()
    url = f"http://localhost:{port}"

    console.print(f"  [bold cyan]Sistema B[/bold cyan] — Interfaz web")
    console.print(f"  🌐 Abriendo en: [bold]{url}[/bold]")
    console.print(f"  [dim]Pulsa Ctrl+C para cerrar[/dim]")
    divider()

    if not no_browser:
        def _open():
            time.sleep(1.5)
            open_url(url)
        threading.Thread(target=_open, daemon=True).start()

    import uvicorn
    uvicorn.run(
        "bp.web.app:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )

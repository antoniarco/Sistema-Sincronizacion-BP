"""Gestion de identidad del usuario."""

from __future__ import annotations

from bp.config.settings import get_settings


def get_current_user() -> str:
    """Devuelve el nombre del usuario configurado."""
    settings = get_settings()
    if not settings.user.nombre:
        from rich.console import Console
        Console(stderr=True).print(
            "[red]Error: No tienes configurado tu nombre.[/red]\n"
            "Ejecuta: bp setup"
        )
        raise SystemExit(1)
    return settings.user.nombre


def get_current_email() -> str:
    """Devuelve el email del usuario configurado."""
    return get_settings().user.email


def is_admin() -> bool:
    """Devuelve True si el usuario tiene rol admin."""
    return get_settings().is_admin

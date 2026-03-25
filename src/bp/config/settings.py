"""Modelo de configuracion de Sistema B.

Compatible con macOS, Linux y Windows:
- macOS:   ~/.config/bp/
- Linux:   $XDG_CONFIG_HOME/bp/ (default: ~/.config/bp/)
- Windows: %APPDATA%/bp/
- Workspace: ~/bp-workspace (todas las plataformas)
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Optional

import tomllib
from pydantic import BaseModel, Field


def _get_config_dir() -> Path:
    """Devuelve el directorio de configuracion segun la plataforma."""
    system = platform.system()
    if system == "Windows":
        # %APPDATA%\bp  (ej: C:\Users\Ana\AppData\Roaming\bp)
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "bp"
        return Path.home() / "AppData" / "Roaming" / "bp"
    # macOS y Linux
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "bp"
    return Path.home() / ".config" / "bp"


CONFIG_DIR = _get_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.toml"


class UserConfig(BaseModel):
    nombre: str = ""
    email: str = ""
    rol: str = Field(default="user", pattern=r"^(user|admin)$")


class RepoConfig(BaseModel):
    url: str = ""
    workspace: str = str(Path.home() / "bp-workspace")


class SlackConfig(BaseModel):
    webhook_url: str = ""
    canal: str = "#bp-control"
    activado: bool = True


class LockConfig(BaseModel):
    expiracion_horas: int = 24
    auto_liberar_tras_push: bool = True


class Settings(BaseModel):
    user: UserConfig = UserConfig()
    repositorio: RepoConfig = RepoConfig()
    slack: SlackConfig = SlackConfig()
    bloqueo: LockConfig = LockConfig()

    @classmethod
    def load(cls) -> Settings:
        """Carga la configuracion desde config.toml."""
        if not CONFIG_FILE.exists():
            return cls()
        try:
            with open(CONFIG_FILE, "rb") as f:
                data = tomllib.load(f)
            return cls.model_validate(data)
        except Exception as e:
            from rich.console import Console
            Console(stderr=True).print(
                f"[yellow]Aviso: No se pudo leer la configuracion ({e}). "
                f"Usando valores por defecto.[/yellow]"
            )
            return cls()

    def save(self) -> None:
        """Guarda la configuracion actual en config.toml."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        lines = [
            "[user]",
            f'nombre = "{self.user.nombre}"',
            f'email = "{self.user.email}"',
            f'rol = "{self.user.rol}"',
            "",
            "[repositorio]",
            f'url = "{self.repositorio.url}"',
            f'workspace = "{self.repositorio.workspace}"',
            "",
            "[slack]",
            f'webhook_url = "{self.slack.webhook_url}"',
            f'canal = "{self.slack.canal}"',
            f"activado = {'true' if self.slack.activado else 'false'}",
            "",
            "[bloqueo]",
            f"expiracion_horas = {self.bloqueo.expiracion_horas}",
            f"auto_liberar_tras_push = {'true' if self.bloqueo.auto_liberar_tras_push else 'false'}",
        ]
        CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    @property
    def workspace_path(self) -> Path:
        return Path(self.repositorio.workspace).expanduser()

    @property
    def bp_dir(self) -> Path:
        return self.workspace_path / ".bp"

    @property
    def state_file(self) -> Path:
        return self.bp_dir / "state.json"

    @property
    def is_admin(self) -> bool:
        return self.user.rol == "admin"


def get_settings() -> Settings:
    """Singleton de configuracion."""
    return Settings.load()

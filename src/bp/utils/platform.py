"""Utilidades cross-platform para macOS, Windows y Linux.

Centraliza toda la logica dependiente del sistema operativo
para que el resto del codigo no necesite hacer comprobaciones.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path, PurePosixPath

SYSTEM = platform.system()  # "Darwin", "Windows", "Linux"


# ── Deteccion de plataforma ───────────────────────────────────────────────

def is_windows() -> bool:
    return SYSTEM == "Windows"


def is_mac() -> bool:
    return SYSTEM == "Darwin"


def is_linux() -> bool:
    return SYSTEM == "Linux"


def platform_name() -> str:
    return {"Darwin": "macOS", "Windows": "Windows", "Linux": "Linux"}.get(SYSTEM, SYSTEM)


# ── Abrir archivos y URLs ────────────────────────────────────────────────

def open_file(path: str | Path) -> None:
    """Abre un archivo con la aplicacion predeterminada del sistema."""
    path = str(path)
    try:
        if is_mac():
            subprocess.Popen(["open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif is_windows():
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass  # No bloquear si falla


def open_url(url: str) -> None:
    """Abre una URL en el navegador predeterminado. Compatible con todos los OS."""
    try:
        webbrowser.open(url)
    except Exception:
        # Fallback manual
        try:
            if is_mac():
                subprocess.Popen(["open", url])
            elif is_windows():
                os.startfile(url)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", url])
        except Exception:
            pass


# ── Operaciones de archivos robustas ─────────────────────────────────────

def safe_rmtree(path: Path, retries: int = 3) -> None:
    """Elimina un directorio con reintentos para Windows (archivos bloqueados).

    En Windows, procesos como Git, Excel o antivirus pueden mantener
    handles abiertos brevemente. Reintentamos con backoff.
    """
    for attempt in range(retries):
        try:
            shutil.rmtree(str(path))
            return
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
            else:
                # Ultimo intento: ignorar errores
                shutil.rmtree(str(path), ignore_errors=True)
        except FileNotFoundError:
            return  # Ya no existe


def safe_move(src: Path, dst: Path, retries: int = 3) -> None:
    """Mueve un directorio con reintentos para Windows (handles abiertos).

    Especialmente necesario para mover .git/ que puede tener
    archivos bloqueados por procesos de Git.
    """
    for attempt in range(retries):
        try:
            shutil.move(str(src), str(dst))
            return
        except (PermissionError, OSError) as e:
            if attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
            else:
                raise OSError(
                    f"No se pudo mover '{src}' a '{dst}' tras {retries} intentos. "
                    f"Cierra cualquier programa que pueda estar usando estos archivos."
                ) from e


# ── Rutas ─────────────────────────────────────────────────────────────────

def to_git_path(path: str | Path) -> str:
    """Convierte una ruta del sistema a formato Git (siempre forward slashes).

    Git SIEMPRE usa forward slashes internamente, incluso en Windows.
    """
    return str(PurePosixPath(Path(path)))


def normalize_rel_path(rel: Path) -> str:
    """Normaliza una ruta relativa a forward slashes para consistencia cross-platform."""
    return str(PurePosixPath(rel))


# ── Archivos ──────────────────────────────────────────────────────────────

def read_text(path: Path) -> str:
    """Lee un archivo de texto con encoding UTF-8 explicito."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """Escribe un archivo de texto con encoding UTF-8 y newlines Unix."""
    path.write_text(content, encoding="utf-8", newline="\n")


def append_line(path: Path, line: str) -> None:
    """Anade una linea a un archivo con encoding UTF-8 y newline Unix."""
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")


# ── Subprocess ────────────────────────────────────────────────────────────

def run_command(args: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    """Ejecuta un comando con encoding UTF-8 explicito."""
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )

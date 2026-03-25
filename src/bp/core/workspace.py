"""Gestion del workspace local. Compatible con macOS, Linux y Windows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from bp.config.settings import Settings
from bp.core import git_ops
from bp.i18n import es
from bp.utils.platform import normalize_rel_path, safe_rmtree, read_text, write_text


# Extensiones de modelos BP soportadas
MODEL_EXTENSIONS = {".xlsx", ".xlsm", ".xls", ".xlsb"}


def init_workspace(settings: Settings) -> None:
    """Inicializa el workspace clonando el repo central."""
    workspace = settings.workspace_path
    if workspace.exists():
        safe_rmtree(workspace)
    git_ops.clone(settings.repositorio.url, workspace)
    _save_state(settings, git_ops.get_head_sha(workspace))


def is_initialized(settings: Settings) -> bool:
    """Verifica si el workspace esta inicializado."""
    git_pointer = settings.workspace_path / ".git"
    git_dir = settings.bp_dir / ".git"
    return git_pointer.exists() or git_dir.exists()


def ensure_initialized(settings: Settings) -> None:
    """Lanza error si el workspace no esta inicializado."""
    if not is_initialized(settings):
        from bp.utils.errors import ConfigError
        raise ConfigError(es.ERR_NO_WORKSPACE)


def get_models(settings: Settings) -> list[Path]:
    """Lista los modelos BP en el workspace."""
    workspace = settings.workspace_path
    models = []
    for ext in MODEL_EXTENSIONS:
        models.extend(workspace.glob(f"*{ext}"))
        models.extend(workspace.glob(f"**/*{ext}"))
    # Excluir archivos en .bp/
    models = [m for m in models if ".bp" not in m.parts]
    return sorted(set(models))


def find_model(settings: Settings, name: str) -> Optional[Path]:
    """Busca un modelo por nombre (con o sin extension)."""
    workspace = settings.workspace_path
    exact = workspace / name
    if exact.exists() and exact.suffix in MODEL_EXTENSIONS:
        return exact
    for model in get_models(settings):
        if model.name == name or model.stem == name:
            return model
    return None


def get_model_checksum(path: Path) -> str:
    """Calcula el SHA256 de un archivo."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def has_local_changes(settings: Settings, model_path: Path) -> bool:
    """Detecta si un modelo tiene cambios locales respecto al ultimo get."""
    state = _load_state(settings)
    rel_path = normalize_rel_path(model_path.relative_to(settings.workspace_path))
    saved_checksum = state.get("checksums", {}).get(rel_path)
    if saved_checksum is None:
        return False
    current_checksum = get_model_checksum(model_path)
    return current_checksum != saved_checksum


def create_backup(model_path: Path) -> Path:
    """Crea una copia de seguridad del modelo."""
    from datetime import datetime
    import shutil
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{model_path.stem}_backup_{timestamp}{model_path.suffix}"
    backup_path = model_path.parent / backup_name
    shutil.copy2(model_path, backup_path)
    return backup_path


def update_state(settings: Settings, head_sha: str) -> None:
    """Actualiza el state.json con el SHA actual y checksums de modelos."""
    _save_state(settings, head_sha)


def _save_state(settings: Settings, head_sha: str) -> None:
    """Guarda el estado local."""
    checksums = {}
    for model in get_models(settings):
        rel_path = normalize_rel_path(model.relative_to(settings.workspace_path))
        checksums[rel_path] = get_model_checksum(model)

    state = {
        "head_sha": head_sha,
        "checksums": checksums,
    }

    settings.bp_dir.mkdir(parents=True, exist_ok=True)
    write_text(settings.state_file, json.dumps(state, indent=2))


def _load_state(settings: Settings) -> dict:
    """Carga el estado local."""
    if not settings.state_file.exists():
        return {}
    try:
        return json.loads(read_text(settings.state_file))
    except (json.JSONDecodeError, OSError):
        return {}


def get_local_head_sha(settings: Settings) -> str:
    """Devuelve el SHA guardado en state.json."""
    state = _load_state(settings)
    return state.get("head_sha", "")

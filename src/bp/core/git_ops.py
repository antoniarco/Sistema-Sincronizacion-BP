"""Capa de abstraccion sobre Git. Ningun otro modulo debe usar git directamente.

Compatible con macOS, Linux y Windows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from git import Repo, GitCommandError

from bp.i18n import es
from bp.utils.errors import NetworkError
from bp.utils.platform import to_git_path, safe_move, write_text


def _get_repo(workspace: Path) -> Repo:
    """Obtiene el repo Git del workspace."""
    git_pointer = workspace / ".git"
    git_dir = workspace / ".bp" / ".git"
    if not git_pointer.exists() and not git_dir.exists():
        raise FileNotFoundError(es.ERR_NO_WORKSPACE)
    return Repo(str(workspace))


def clone(repo_url: str, workspace: Path) -> Repo:
    """Clona el repositorio central al workspace local."""
    try:
        repo = Repo.clone_from(repo_url, str(workspace), branch="main")
        # Mover .git dentro de .bp/ para ocultarlo del usuario
        bp_dir = workspace / ".bp"
        bp_dir.mkdir(parents=True, exist_ok=True)
        git_dir = workspace / ".git"
        target_git_dir = bp_dir / ".git"
        if git_dir.is_dir():
            safe_move(git_dir, target_git_dir)
            # Git requiere forward slashes en el .git pointer file (todas las plataformas)
            write_text(git_dir, "gitdir: .bp/.git\n")
        return Repo(str(workspace))
    except GitCommandError as e:
        raise NetworkError(es.ERR_NETWORK) from e


def fetch(workspace: Path) -> None:
    """Descarga los cambios del remoto sin aplicarlos."""
    repo = _get_repo(workspace)
    try:
        repo.remotes.origin.fetch()
    except GitCommandError as e:
        raise NetworkError(es.ERR_NETWORK) from e


def pull(workspace: Path) -> str:
    """Actualiza el workspace con la ultima version. Devuelve el nuevo HEAD SHA."""
    repo = _get_repo(workspace)
    try:
        repo.remotes.origin.pull("main", ff_only=True)
        return repo.head.commit.hexsha
    except GitCommandError as e:
        raise NetworkError(es.ERR_NETWORK) from e


def commit_and_push(workspace: Path, files: list[str], message: str) -> str:
    """Hace commit de archivos y push al remoto. Devuelve el SHA del commit."""
    repo = _get_repo(workspace)
    try:
        # Normalizar rutas a formato git (forward slashes en todas las plataformas)
        files = [to_git_path(f) for f in files]
        # Separar archivos existentes de eliminados
        existing = [f for f in files if (workspace / f).exists()]
        deleted = [f for f in files if not (workspace / f).exists()]
        if existing:
            repo.index.add(existing)
        if deleted:
            try:
                repo.index.remove(deleted)
            except Exception:
                pass  # Ya eliminado del indice
        commit = repo.index.commit(message)
        repo.remotes.origin.push("main")
        return commit.hexsha
    except GitCommandError as e:
        if "rejected" in str(e).lower() or "non-fast-forward" in str(e).lower():
            return ""
        raise NetworkError(es.ERR_NETWORK) from e


def get_head_sha(workspace: Path) -> str:
    """Devuelve el SHA del HEAD local."""
    repo = _get_repo(workspace)
    return repo.head.commit.hexsha


def get_remote_head_sha(workspace: Path) -> str:
    """Devuelve el SHA del HEAD remoto (requiere fetch previo)."""
    repo = _get_repo(workspace)
    try:
        return str(repo.remotes.origin.refs.main.commit.hexsha)
    except (IndexError, AttributeError):
        return repo.head.commit.hexsha


def get_log(workspace: Path, model: Optional[str] = None, limit: int = 20) -> list[dict]:
    """Devuelve el historial de commits."""
    repo = _get_repo(workspace)
    entries = []
    kwargs = {"max_count": limit}
    if model:
        kwargs["paths"] = model
    for commit in repo.iter_commits("main", **kwargs):
        entries.append({
            "sha": commit.hexsha[:8],
            "author": commit.author.name,
            "date": commit.committed_datetime.strftime("%d/%m/%Y %H:%M"),
            "message": commit.message.strip(),
        })
    return entries


def get_file_at_version(workspace: Path, file_path: str, sha: str) -> Optional[bytes]:
    """Devuelve el contenido de un archivo en una version especifica."""
    repo = _get_repo(workspace)
    try:
        commit = repo.commit(sha)
        blob = commit.tree / file_path
        return blob.data_stream.read()
    except (KeyError, GitCommandError):
        return None


def stage_deletion(workspace: Path, files: list[str]) -> None:
    """Marca archivos para eliminacion en el proximo commit."""
    repo = _get_repo(workspace)
    repo.index.remove(files, working_tree=True, r=True)


def has_remote(workspace: Path) -> bool:
    """Verifica si el repo tiene un remoto configurado."""
    try:
        repo = _get_repo(workspace)
        return len(repo.remotes) > 0
    except FileNotFoundError:
        return False

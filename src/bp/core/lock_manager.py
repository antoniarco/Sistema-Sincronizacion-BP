"""Gestor de bloqueos atomicos para modelos BP. Cross-platform."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from bp.config.settings import Settings
from bp.core import git_ops
from bp.i18n import es
from bp.utils.errors import LockError
from bp.utils.platform import to_git_path, read_text, write_text

LOCKS_DIR = ".bp-locks"
MAX_RETRIES = 3


class LockInfo:
    """Informacion de un bloqueo activo."""

    def __init__(self, model: str, locked_by: str, locked_at: str, expires_at: str, comment: str = ""):
        self.model = model
        self.locked_by = locked_by
        self.locked_at = datetime.fromisoformat(locked_at)
        self.expires_at = datetime.fromisoformat(expires_at)
        self.comment = comment

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def hours_held(self) -> int:
        delta = datetime.now(timezone.utc) - self.locked_at
        return int(delta.total_seconds() / 3600)

    @property
    def since_str(self) -> str:
        return self.locked_at.strftime("%d/%m/%Y %H:%M")

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "locked_by": self.locked_by,
            "locked_at": self.locked_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: dict) -> LockInfo:
        return cls(**data)


def _lock_file_path(workspace: Path, model: str) -> Path:
    return workspace / LOCKS_DIR / f"{model}.lock.json"


def _lock_git_path(model: str) -> str:
    """Ruta relativa del lock en formato git (forward slashes siempre)."""
    return to_git_path(f"{LOCKS_DIR}/{model}.lock.json")


def _read_lock(workspace: Path, model: str) -> Optional[LockInfo]:
    lock_path = _lock_file_path(workspace, model)
    if not lock_path.exists():
        return None
    try:
        data = json.loads(read_text(lock_path))
        return LockInfo.from_dict(data)
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def _write_lock(workspace: Path, lock_info: LockInfo) -> None:
    lock_dir = workspace / LOCKS_DIR
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = _lock_file_path(workspace, lock_info.model)
    write_text(lock_path, json.dumps(lock_info.to_dict(), indent=2))


def _delete_lock_file(workspace: Path, model: str) -> None:
    lock_path = _lock_file_path(workspace, model)
    if lock_path.exists():
        lock_path.unlink()


def check_lock(settings: Settings, model: str) -> Optional[LockInfo]:
    """Comprueba el estado del lock de un modelo (hace fetch primero)."""
    workspace = settings.workspace_path
    git_ops.fetch(workspace)
    lock = _read_lock(workspace, model)
    if lock and lock.is_expired:
        _auto_expire_lock(settings, lock)
        return None
    return lock


def acquire_lock(settings: Settings, model: str, user: str) -> LockInfo:
    """Intenta adquirir el lock. Reintenta en caso de race condition."""
    workspace = settings.workspace_path

    for attempt in range(MAX_RETRIES):
        git_ops.fetch(workspace)

        existing = _read_lock(workspace, model)
        if existing and not existing.is_expired:
            raise LockError(
                es.ERR_LOCK_DENIED.format(
                    model=model, user=existing.locked_by, since=existing.since_str,
                )
            )

        if existing and existing.is_expired:
            _delete_lock_file(workspace, model)

        now = datetime.now(timezone.utc)
        expiry = now + timedelta(hours=settings.bloqueo.expiracion_horas)

        lock_info = LockInfo(
            model=model, locked_by=user,
            locked_at=now.isoformat(), expires_at=expiry.isoformat(),
        )
        _write_lock(workspace, lock_info)

        sha = git_ops.commit_and_push(
            workspace,
            [_lock_git_path(model)],
            f"lock: {user} reserva {model}",
        )

        if sha:
            return lock_info

        git_ops.pull(workspace)

    raise LockError(es.ERR_RACE_CONDITION)


def release_lock(settings: Settings, model: str, user: str, force: bool = False) -> None:
    """Libera el lock de un modelo."""
    workspace = settings.workspace_path
    git_ops.fetch(workspace)

    existing = _read_lock(workspace, model)
    if not existing:
        raise LockError(es.ERR_LOCK_NOT_FOUND.format(model=model))

    if not force and existing.locked_by != user:
        raise LockError(
            es.ERR_LOCK_NOT_OWNED.format(model=model, user=existing.locked_by)
        )

    _delete_lock_file(workspace, model)

    action = "force-unlock" if force else "unlock"
    git_ops.commit_and_push(
        workspace,
        [_lock_git_path(model)],
        f"{action}: {user} libera {model}",
    )


def get_all_locks(settings: Settings) -> list[LockInfo]:
    """Devuelve todos los locks activos."""
    workspace = settings.workspace_path
    lock_dir = workspace / LOCKS_DIR
    if not lock_dir.exists():
        return []

    locks = []
    for lock_file in lock_dir.glob("*.lock.json"):
        try:
            data = json.loads(read_text(lock_file))
            lock = LockInfo.from_dict(data)
            if not lock.is_expired:
                locks.append(lock)
        except (json.JSONDecodeError, KeyError):
            continue
    return locks


def _auto_expire_lock(settings: Settings, lock: LockInfo) -> None:
    workspace = settings.workspace_path
    _delete_lock_file(workspace, lock.model)

    git_ops.commit_and_push(
        workspace,
        [_lock_git_path(lock.model)],
        f"auto-expire: reserva de {lock.locked_by} sobre {lock.model} expirada",
    )

    from bp.core.slack import notify_lock_expired
    notify_lock_expired(settings, lock.locked_by, lock.model)

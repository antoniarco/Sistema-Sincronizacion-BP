"""Deteccion de versiones obsoletas y seguimiento de versiones. Cross-platform."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from bp.config.settings import Settings
from bp.core import git_ops
from bp.core.workspace import get_local_head_sha
from bp.utils.platform import read_text, append_line

HISTORY_FILE = ".bp-meta/history.jsonl"


class VersionEntry:
    def __init__(self, version: int, model: str, author: str, date: str,
                 comment: str, action: str = "push", sha: str = ""):
        self.version = version
        self.model = model
        self.author = author
        self.date = date
        self.comment = comment
        self.action = action
        self.sha = sha

    def to_dict(self) -> dict:
        return {
            "version": self.version, "model": self.model, "author": self.author,
            "date": self.date, "comment": self.comment, "action": self.action,
            "sha": self.sha,
        }

    @classmethod
    def from_dict(cls, data: dict) -> VersionEntry:
        return cls(**data)


def is_version_current(settings: Settings) -> bool:
    workspace = settings.workspace_path
    local_sha = get_local_head_sha(settings)
    if not local_sha:
        return False
    git_ops.fetch(workspace)
    remote_sha = git_ops.get_remote_head_sha(workspace)
    return local_sha == remote_sha


def get_remote_version_info(settings: Settings) -> Optional[dict]:
    workspace = settings.workspace_path
    log = git_ops.get_log(workspace, limit=1)
    return log[0] if log else None


def get_next_version(settings: Settings, model: str) -> int:
    entries = read_history(settings, model)
    if not entries:
        return 1
    return max(e.version for e in entries) + 1


def append_history(settings: Settings, entry: VersionEntry) -> None:
    workspace = settings.workspace_path
    history_path = workspace / HISTORY_FILE
    history_path.parent.mkdir(parents=True, exist_ok=True)
    append_line(history_path, json.dumps(entry.to_dict()))


def read_history(settings: Settings, model: Optional[str] = None,
                 limit: int = 50) -> list[VersionEntry]:
    workspace = settings.workspace_path
    history_path = workspace / HISTORY_FILE
    if not history_path.exists():
        return []

    entries = []
    for line in read_text(history_path).strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            entry = VersionEntry.from_dict(data)
            if model is None or entry.model == model:
                entries.append(entry)
        except (json.JSONDecodeError, KeyError):
            continue

    entries.sort(key=lambda e: e.version, reverse=True)
    return entries[:limit]


def get_version_by_number(settings: Settings, model: str, version: int) -> Optional[VersionEntry]:
    entries = read_history(settings, model, limit=1000)
    for entry in entries:
        if entry.version == version:
            return entry
    return None

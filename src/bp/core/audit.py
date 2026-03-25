"""Log de auditoria para acciones administrativas. Cross-platform."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from bp.config.settings import Settings
from bp.utils.platform import read_text, append_line

AUDIT_FILE = ".bp-meta/audit.jsonl"


class AuditEntry:
    def __init__(self, action: str, user: str, model: str, detail: str = "",
                 timestamp: str = ""):
        self.action = action
        self.user = user
        self.model = model
        self.detail = detail
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "action": self.action, "user": self.user, "model": self.model,
            "detail": self.detail, "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AuditEntry:
        return cls(**data)

    @property
    def date_str(self) -> str:
        dt = datetime.fromisoformat(self.timestamp)
        return dt.strftime("%d/%m/%Y %H:%M")


def log_action(settings: Settings, entry: AuditEntry) -> None:
    workspace = settings.workspace_path
    audit_path = workspace / AUDIT_FILE
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    append_line(audit_path, json.dumps(entry.to_dict()))


def read_audit_log(settings: Settings, limit: int = 50) -> list[AuditEntry]:
    workspace = settings.workspace_path
    audit_path = workspace / AUDIT_FILE
    if not audit_path.exists():
        return []

    entries = []
    for line in read_text(audit_path).strip().split("\n"):
        if not line:
            continue
        try:
            entries.append(AuditEntry.from_dict(json.loads(line)))
        except (json.JSONDecodeError, KeyError):
            continue

    entries.reverse()
    return entries[:limit]

"""Integracion con Slack via webhooks."""

from __future__ import annotations

from bp.config.settings import Settings
from bp.i18n import es


def _send(settings: Settings, text: str) -> None:
    """Envia un mensaje al webhook de Slack. Fallo silencioso."""
    if not settings.slack.activado or not settings.slack.webhook_url:
        return

    try:
        import httpx
        httpx.post(
            settings.slack.webhook_url,
            json={"text": text, "channel": settings.slack.canal},
            timeout=5.0,
        )
    except Exception:
        # Slack no debe bloquear la operacion del usuario
        pass


def notify_lock(settings: Settings, user: str, model: str) -> None:
    _send(settings, es.SLACK_LOCK.format(user=user, model=model))


def notify_unlock(settings: Settings, user: str, model: str) -> None:
    _send(settings, es.SLACK_UNLOCK.format(user=user, model=model))


def notify_push(settings: Settings, user: str, model: str, comment: str) -> None:
    _send(settings, es.SLACK_PUSH.format(user=user, model=model, comment=comment))


def notify_force_unlock(settings: Settings, admin: str, user: str, model: str) -> None:
    _send(settings, es.SLACK_FORCE_UNLOCK.format(admin=admin, user=user, model=model))


def notify_revert(settings: Settings, user: str, model: str, version: int) -> None:
    _send(settings, es.SLACK_REVERT.format(user=user, model=model, version=version))


def notify_lock_expired(settings: Settings, user: str, model: str) -> None:
    _send(settings, es.SLACK_LOCK_EXPIRED.format(user=user, model=model))

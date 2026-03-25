"""Excepciones personalizadas de Sistema B."""


class BPError(Exception):
    """Error base de Sistema B. El mensaje se muestra al usuario."""
    pass


class NetworkError(BPError):
    """Error de conexion con el repositorio central."""
    pass


class LockError(BPError):
    """Error relacionado con el sistema de bloqueo."""
    pass


class VersionError(BPError):
    """Error de version (desactualizada, no encontrada, etc.)."""
    pass


class ConfigError(BPError):
    """Error de configuracion."""
    pass


class PermissionError_(BPError):
    """Error de permisos (no es admin)."""
    pass

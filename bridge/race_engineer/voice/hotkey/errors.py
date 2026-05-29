class HotkeyError(Exception):
    """Base error for global hotkey handling."""


class HotkeyRegistrationError(HotkeyError):
    """Raised when the global hotkey listener cannot be started."""


class HotkeyConflictError(HotkeyError):
    """Raised when a hotkey binding cannot be applied due to a conflict."""

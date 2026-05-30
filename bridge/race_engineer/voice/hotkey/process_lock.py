from __future__ import annotations

import atexit
import ctypes
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_LOCK_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "race-engineer"
_LOCK_FILENAME = "voice_hotkey.lock"
_WINDOWS_MUTEX_NAME = "Local\\RaceEngineerVoiceHotkeyV1"
_ERROR_ALREADY_EXISTS = 183
DEFAULT_LOCK_RETRY_ATTEMPTS = 10
DEFAULT_LOCK_RETRY_DELAY_SECONDS = 0.5

def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


class _WindowsMutex:
    def __init__(self, name: str) -> None:
        self._name = name
        self._handle: int | None = None
        self._held = False

    def acquire(self) -> bool:
        if self._held:
            return True

        kernel32 = ctypes.windll.kernel32
        kernel32.SetLastError(0)
        handle = kernel32.CreateMutexW(None, True, self._name)
        if not handle:
            logger.warning("failed to create voice hotkey mutex")
            return False

        already_exists = kernel32.GetLastError() == _ERROR_ALREADY_EXISTS
        if already_exists:
            kernel32.CloseHandle(handle)
            return False
        self._handle = handle
        self._held = True
        atexit.register(self.release)
        logger.info("voice hotkey mutex acquired (pid %s)", os.getpid())
        return True

    def release(self) -> None:
        if not self._held or self._handle is None:
            return

        kernel32 = ctypes.windll.kernel32
        kernel32.ReleaseMutex(self._handle)
        kernel32.CloseHandle(self._handle)
        self._handle = None
        self._held = False


class VoiceHotkeyProcessLock:
    """Ensure only one bridge process owns the global push-to-talk listener."""

    def __init__(self, lock_path: Path | None = None) -> None:
        self._lock_path = lock_path or (_DEFAULT_LOCK_DIR / _LOCK_FILENAME)
        self._held = False
        self._windows_mutex = (
            _WindowsMutex(_WINDOWS_MUTEX_NAME)
            if os.name == "nt" and lock_path is None
            else None
        )

    @property
    def lock_path(self) -> Path:
        return self._lock_path

    def acquire(
        self,
        *,
        retry_attempts: int = 1,
        retry_delay_seconds: float = DEFAULT_LOCK_RETRY_DELAY_SECONDS,
    ) -> bool:
        if self._held:
            return True

        attempts = max(1, retry_attempts)
        for attempt in range(1, attempts + 1):
            if self._try_acquire_once():
                return True

            if attempt < attempts:
                logger.info(
                    "voice hotkey lock busy; retrying in %.1fs (%s/%s)",
                    retry_delay_seconds,
                    attempt,
                    attempts,
                )
                time.sleep(retry_delay_seconds)

        logger.warning(
            "voice hotkey lock unavailable after %s attempts (pid %s)",
            attempts,
            os.getpid(),
        )
        return False

    def _try_acquire_once(self) -> bool:
        if self._windows_mutex is not None:
            if not self._windows_mutex.acquire():
                return False
            self._held = True
            return True

        return self._acquire_file_lock()

    def release(self) -> None:
        if not self._held:
            return

        self._held = False
        if self._windows_mutex is not None:
            self._windows_mutex.release()
            return

        try:
            self._lock_path.unlink(missing_ok=True)
        except OSError:
            logger.debug("failed to remove voice hotkey lock", exc_info=True)

    def _acquire_file_lock(self) -> bool:
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        if self._lock_path.exists() and not self._try_claim_stale():
            logger.warning(
                "voice hotkey lock held by another bridge process (%s)",
                self._lock_path,
            )
            return False

        try:
            fd = os.open(self._lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            logger.warning(
                "voice hotkey lock already held by another bridge process (%s)",
                self._lock_path,
            )
            return False

        try:
            os.write(fd, str(os.getpid()).encode("ascii"))
        finally:
            os.close(fd)

        self._held = True
        atexit.register(self.release)
        logger.info("voice hotkey lock acquired (pid %s)", os.getpid())
        return True

    def _try_claim_stale(self) -> bool:
        try:
            raw = self._lock_path.read_text(encoding="ascii").strip()
            pid = int(raw)
        except (OSError, ValueError):
            pid = -1

        if _pid_alive(pid):
            return False

        logger.info("removing stale voice hotkey lock (pid %s)", pid)
        try:
            self._lock_path.unlink(missing_ok=True)
        except OSError:
            return False
        return True

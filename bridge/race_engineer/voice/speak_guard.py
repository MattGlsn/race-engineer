from __future__ import annotations

import hashlib
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_LOCK_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "race-engineer"
DEFAULT_DEDUPE_WINDOW_SECONDS = 12.0


class SpeakGuard:
    """Suppress duplicate engineer TTS playback across bridge processes."""

    def __init__(
        self,
        lock_dir: Path | None = None,
        *,
        window_seconds: float = DEFAULT_DEDUPE_WINDOW_SECONDS,
    ) -> None:
        self._lock_dir = lock_dir or _DEFAULT_LOCK_DIR
        self._window_seconds = window_seconds

    def claim(self, text: str) -> bool:
        """Return True when playback should proceed, False for a recent duplicate."""
        normalized = text.strip()
        if not normalized:
            return False

        self._lock_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
        claim_path = self._lock_dir / f"speak-{digest}.lock"
        now = time.time()

        if claim_path.exists():
            if self._claim_is_fresh(claim_path, now):
                logger.info(
                    "skipping duplicate engineer speech (pid=%s): %r",
                    os.getpid(),
                    normalized[:80],
                )
                return False
            try:
                claim_path.unlink(missing_ok=True)
            except OSError:
                logger.debug("failed to remove stale speak claim", exc_info=True)
                return False

        try:
            fd = os.open(claim_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if claim_path.exists() and self._claim_is_fresh(claim_path, now):
                logger.info(
                    "skipping duplicate engineer speech (pid=%s): %r",
                    os.getpid(),
                    normalized[:80],
                )
                return False
            return False

        try:
            os.write(fd, f"{now}\n{os.getpid()}".encode("ascii"))
        finally:
            os.close(fd)

        return True

    def _claim_is_fresh(self, claim_path: Path, now: float) -> bool:
        try:
            raw = claim_path.read_text(encoding="ascii").splitlines()
            claimed_at = float(raw[0])
        except (OSError, ValueError, IndexError):
            return False
        return (now - claimed_at) < self._window_seconds

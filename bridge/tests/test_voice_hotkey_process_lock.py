import os
from pathlib import Path
from unittest.mock import patch

import pytest

from race_engineer.voice.hotkey.process_lock import VoiceHotkeyProcessLock


@pytest.fixture
def lock_path(tmp_path: Path) -> Path:
    return tmp_path / "voice_hotkey.lock"


def test_acquire_creates_lock_file(lock_path: Path) -> None:
    lock = VoiceHotkeyProcessLock(lock_path)

    assert lock.acquire() is True
    assert lock_path.read_text(encoding="ascii") == str(os.getpid())

    lock.release()
    assert not lock_path.exists()


def test_second_acquire_fails_while_pid_alive(lock_path: Path) -> None:
    first = VoiceHotkeyProcessLock(lock_path)
    second = VoiceHotkeyProcessLock(lock_path)

    assert first.acquire() is True
    assert second.acquire() is False

    first.release()


def test_acquire_retries_until_lock_is_free(lock_path: Path) -> None:
    first = VoiceHotkeyProcessLock(lock_path)
    second = VoiceHotkeyProcessLock(lock_path)

    assert first.acquire(retry_attempts=1) is True
    assert second.acquire(retry_attempts=1) is False

    first.release()
    assert second.acquire(retry_attempts=3, retry_delay_seconds=0.01) is True
    second.release()


def test_stale_lock_is_reclaimed(lock_path: Path) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("999999999", encoding="ascii")

    lock = VoiceHotkeyProcessLock(lock_path)

    with patch(
        "race_engineer.voice.hotkey.process_lock._pid_alive",
        return_value=False,
    ):
        assert lock.acquire() is True

    assert lock_path.read_text(encoding="ascii") == str(os.getpid())

    lock.release()

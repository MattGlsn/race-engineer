from pathlib import Path

import pytest

from race_engineer.voice.speak_guard import SpeakGuard


@pytest.fixture
def lock_dir(tmp_path: Path) -> Path:
    return tmp_path / "speak-guard"


def test_claim_allows_first_playback(lock_dir: Path) -> None:
    guard = SpeakGuard(lock_dir, window_seconds=5.0)

    assert guard.claim("Copy. P3.") is True


def test_claim_blocks_duplicate_within_window(lock_dir: Path) -> None:
    guard = SpeakGuard(lock_dir, window_seconds=5.0)

    assert guard.claim("Copy. P3.") is True
    assert guard.claim("Copy. P3.") is False


def test_claim_allows_different_text(lock_dir: Path) -> None:
    guard = SpeakGuard(lock_dir, window_seconds=5.0)

    assert guard.claim("Copy. P3.") is True
    assert guard.claim("Fuel looks good.") is True

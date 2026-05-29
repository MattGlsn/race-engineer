import logging

import pytest

from race_engineer.ai.llm.errors import LlmErrorCode
from race_engineer.ai.llm.metadata import CompletionMetadata, log_completion_metadata


def test_log_completion_metadata_excludes_sensitive_content(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)

    log_completion_metadata(
        CompletionMetadata(
            context_bytes=512,
            response_word_count=12,
            model="gpt-4o-mini",
            latency_ms=180,
            prompt_tokens=120,
            completion_tokens=18,
            fallback_used=False,
        )
    )

    assert len(caplog.records) == 1
    message = caplog.records[0].getMessage()
    assert "gpt-4o-mini" in message
    assert "context_bytes=512" in message
    assert "response_word_count=12" in message
    assert "Driver message" not in message
    assert "Race context JSON" not in message


def test_log_completion_metadata_includes_error_code_on_fallback(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)

    log_completion_metadata(
        CompletionMetadata(
            context_bytes=128,
            response_word_count=10,
            fallback_used=True,
            error_code=LlmErrorCode.TIMEOUT,
        )
    )

    message = caplog.records[0].getMessage()
    assert "fallback_used=True" in message
    assert "error_code=timeout" in message

import os
from dataclasses import dataclass

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com"
DEFAULT_LLM_TIMEOUT_SECONDS = 8.0
DEFAULT_MAX_COMPLETION_TOKENS = 150


@dataclass(frozen=True, slots=True)
class OpenAiLlmConfig:
    api_key: str
    model: str = DEFAULT_OPENAI_MODEL
    base_url: str = DEFAULT_OPENAI_BASE_URL
    timeout_seconds: float = DEFAULT_LLM_TIMEOUT_SECONDS
    max_completion_tokens: int = DEFAULT_MAX_COMPLETION_TOKENS


def load_openai_llm_config() -> OpenAiLlmConfig | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    model = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL)
    timeout_raw = os.environ.get("LLM_TIMEOUT_SECONDS")
    timeout_seconds = (
        float(timeout_raw) if timeout_raw else DEFAULT_LLM_TIMEOUT_SECONDS
    )
    max_tokens_raw = os.environ.get("LLM_MAX_COMPLETION_TOKENS")
    max_completion_tokens = (
        int(max_tokens_raw) if max_tokens_raw else DEFAULT_MAX_COMPLETION_TOKENS
    )
    return OpenAiLlmConfig(
        api_key=api_key,
        model=model,
        base_url=base_url.rstrip("/"),
        timeout_seconds=timeout_seconds,
        max_completion_tokens=max_completion_tokens,
    )

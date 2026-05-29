from enum import StrEnum


class LlmErrorCode(StrEnum):
    TIMEOUT = "timeout"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    INVALID_API_KEY = "invalid_api_key"
    PROVIDER_ERROR = "provider_error"

from enum import StrEnum


class VoiceErrorCode(StrEnum):
    PERMISSION_DENIED = "permission_denied"
    EMPTY_AUDIO = "empty_audio"
    AUDIO_TOO_SHORT = "audio_too_short"
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    INVALID_API_KEY = "invalid_api_key"
    PROVIDER_ERROR = "provider_error"

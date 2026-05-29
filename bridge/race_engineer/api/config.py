import os
from pathlib import Path

from dotenv import load_dotenv

_BRIDGE_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]


def load_env() -> None:
    load_dotenv(_BRIDGE_ROOT / ".env", override=False)


def get_cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "")
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return DEFAULT_CORS_ORIGINS

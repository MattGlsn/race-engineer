from typing import Any

import yaml


def load_session_yaml(text: str) -> dict[str, Any]:
    """Parse iRacing session YAML text into a dictionary."""
    if not text or not text.strip():
        return {}

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}

    if not isinstance(data, dict):
        return {}

    return data

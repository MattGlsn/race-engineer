from typing import Any

from race_engineer.sdk.wrapper import IrSdkWrapper
from race_engineer.session.models import Session
from race_engineer.session.parser import parse_session
from race_engineer.session.yaml_loader import load_session_yaml

SESSION_INFO_KEYS = ("WeekendInfo", "SessionInfo", "DriverInfo")


class SessionInfoReader:
    """Reads and parses iRacing session metadata from the SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def read(self, session_num: int | None = None) -> Session:
        """Read session metadata when connected; otherwise return an empty Session."""
        if not self._sdk.is_connected:
            return Session()

        resolved_session_num = (
            session_num if session_num is not None else self._read_session_num()
        )
        data = self._load_session_data()
        return parse_session(data, session_num=resolved_session_num)

    def _load_session_data(self) -> dict[str, Any]:
        yaml_text = self._sdk.get_session_info_yaml()
        if yaml_text:
            data = load_session_yaml(yaml_text)
            if data:
                return data

        return self._collect_session_info_dict()

    def _collect_session_info_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for key in SESSION_INFO_KEYS:
            value = self._sdk.get_session_info(key)
            if value is not None:
                data[key] = value
        return data

    def _read_session_num(self) -> int:
        value = self._sdk.get_var("SessionNum")
        if value is None:
            return 0

        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

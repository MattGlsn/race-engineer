from unittest.mock import MagicMock

import pytest

from race_engineer.fuel.models import FuelConsumptionSnapshot
from race_engineer.fuel.projection.engine import FuelProjectionEngine
from race_engineer.fuel.projection.models import FuelRiskLevel
from race_engineer.fuel.projection.risk import classify_fuel_risk, fuel_warning_active
from race_engineer.fuel.projection.session_laps import SessionLapsReader
from race_engineer.sdk.wrapper import IrSdkWrapper


@pytest.mark.parametrize(
    ("projected_finish", "avg_usage", "expected"),
    [
        (5.0, 1.5, FuelRiskLevel.SAFE),
        (1.0, 1.5, FuelRiskLevel.CAUTION),
        (0.0, 1.5, FuelRiskLevel.CRITICAL),
        (-0.5, 1.5, FuelRiskLevel.CRITICAL),
        (None, 1.5, FuelRiskLevel.UNKNOWN),
    ],
)
def test_classify_fuel_risk(
    projected_finish: float | None,
    avg_usage: float | None,
    expected: FuelRiskLevel,
) -> None:
    assert classify_fuel_risk(projected_finish, avg_usage) == expected


@pytest.mark.parametrize(
    ("risk_level", "expected"),
    [
        (FuelRiskLevel.SAFE, False),
        (FuelRiskLevel.CAUTION, True),
        (FuelRiskLevel.CRITICAL, True),
        (FuelRiskLevel.UNKNOWN, False),
    ],
)
def test_fuel_warning_active(risk_level: FuelRiskLevel, expected: bool) -> None:
    assert fuel_warning_active(risk_level) == expected


def _mock_sdk(var_map: dict[str, object]) -> MagicMock:
    mock = MagicMock(spec=IrSdkWrapper)
    mock.is_connected = True

    def get_var(name: str) -> object:
        return var_map.get(name)

    mock.get_var.side_effect = get_var
    return mock


def test_projection_engine() -> None:
    engine = FuelProjectionEngine(
        session_laps_reader=SessionLapsReader(
            sdk=_mock_sdk({"SessionLapsRemainEx": 10}),
        ),
    )

    snapshot = engine.project(
        30.0,
        FuelConsumptionSnapshot(rolling_avg_usage=1.5, valid_lap_count=3),
    )

    assert snapshot.laps_remaining == 10
    assert snapshot.projected_finish_fuel == 15.0
    assert snapshot.risk_level == FuelRiskLevel.SAFE
    assert snapshot.warning is False

from race_engineer.availability.checker import VariableAvailabilityChecker
from race_engineer.availability.models import VariableAvailabilityReport
from race_engineer.availability.requirements import (
    OPTIONAL_VARIABLES,
    REQUIRED_VARIABLES,
)


def test_all_variables_available() -> None:
    available = frozenset(REQUIRED_VARIABLES + OPTIONAL_VARIABLES)
    checker = VariableAvailabilityChecker()

    report = checker.check(available)

    assert report.is_fully_available
    assert report.missing_required == ()
    assert report.missing_optional == ()


def test_missing_required_variables() -> None:
    available = frozenset(OPTIONAL_VARIABLES)
    checker = VariableAvailabilityChecker()

    report = checker.check(available)

    assert report.has_missing_required
    assert set(report.missing_required) == set(REQUIRED_VARIABLES)
    assert report.missing_optional == ()


def test_missing_optional_variables() -> None:
    available = frozenset(REQUIRED_VARIABLES)
    checker = VariableAvailabilityChecker()

    report = checker.check(available)

    assert not report.has_missing_required
    assert report.has_missing_optional
    assert set(report.missing_optional) == set(OPTIONAL_VARIABLES)
    assert report.missing_required == ()

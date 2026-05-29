import logging

from race_engineer.availability.models import VariableAvailabilityReport
from race_engineer.availability.report import log_report


def test_log_report_emits_warnings(caplog) -> None:
    report = VariableAvailabilityReport(
        available=frozenset({"Speed"}),
        missing_required=("RPM",),
        missing_optional=("CarIdxPosition",),
    )

    with caplog.at_level(logging.WARNING):
        log_report(report)

    assert "Missing required SDK variables: RPM" in caplog.text
    assert "Missing optional SDK variables: CarIdxPosition" in caplog.text


def test_log_report_skips_when_fully_available(caplog) -> None:
    report = VariableAvailabilityReport(
        available=frozenset({"Speed", "RPM"}),
        missing_required=(),
        missing_optional=(),
    )

    with caplog.at_level(logging.WARNING):
        log_report(report)

    assert caplog.text == ""

import logging

from race_engineer.availability.models import VariableAvailabilityReport

logger = logging.getLogger(__name__)


def log_report(report: VariableAvailabilityReport) -> None:
    """Log user-facing warnings for missing SDK variables."""
    for warning in report.warnings:
        logger.warning(warning)

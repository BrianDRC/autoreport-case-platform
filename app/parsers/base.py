from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class Severity(str, Enum):
    NONE = "NONE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class NormalizedScanResult:
    critical_vulns: int
    high_vulns: int
    critical_misconfig: int
    high_misconfig: int
    max_severity: Severity

    @property
    def critical_count(self) -> int:
        return self.critical_vulns + self.critical_misconfig

    @property
    def high_count(self) -> int:
        return self.high_vulns + self.high_misconfig


class BaseScanParser:
    provider: str  # e.g. "trivy"

    def parse(self, report: Dict[str, Any]) -> NormalizedScanResult:
        raise NotImplementedError

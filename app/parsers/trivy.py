from typing import Any, Dict

from .base import BaseScanParser, NormalizedScanResult, Severity


class TrivyScanParser(BaseScanParser):
    provider = "trivy"

    def parse(self, report: Dict[str, Any]) -> NormalizedScanResult:
        critical_vulns = 0
        high_vulns = 0
        critical_misconfig = 0
        high_misconfig = 0
        max_sev = Severity.NONE

        results = report.get("Results", []) or []

        for result in results:
            # Vulnerabilities
            for vuln in (result.get("Vulnerabilities", []) or []):
                sev = str(vuln.get("Severity", "")).upper()
                if sev == "CRITICAL":
                    critical_vulns += 1
                    max_sev = Severity.CRITICAL
                elif sev == "HIGH":
                    high_vulns += 1
                    if max_sev != Severity.CRITICAL:
                        max_sev = Severity.HIGH

            # Misconfigurations
            for mis in (result.get("Misconfigurations", []) or []):
                sev = str(mis.get("Severity", "")).upper()
                if sev == "CRITICAL":
                    critical_misconfig += 1
                    max_sev = Severity.CRITICAL
                elif sev == "HIGH":
                    high_misconfig += 1
                    if max_sev != Severity.CRITICAL:
                        max_sev = Severity.HIGH

        return NormalizedScanResult(
            critical_vulns=critical_vulns,
            high_vulns=high_vulns,
            critical_misconfig=critical_misconfig,
            high_misconfig=high_misconfig,
            max_severity=max_sev,
        )

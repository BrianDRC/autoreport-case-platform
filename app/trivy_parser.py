from typing import Dict, Any

SEVERITY_ORDER = ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

def get_higher_severity(current: str, new: str) -> str:
    if SEVERITY_ORDER.index(new) > SEVERITY_ORDER.index(current):
        return new
    return current

def parse_trivy_report(report: Dict[str, Any]) -> Dict[str, Any]:
    critical_count = 0
    high_count = 0
    max_severity = "LOW"

    results = report.get("Results", [])

    for result in results:

        # Vulnerabilities
        vulnerabilities = result.get("Vulnerabilities", [])
        for vuln in vulnerabilities:
            severity = vuln.get("Severity", "UNKNOWN").upper()

            if severity == "CRITICAL":
                critical_count += 1
                max_severity = get_higher_severity(max_severity, severity)

            elif severity == "HIGH":
                high_count += 1
                max_severity = get_higher_severity(max_severity, severity)

        # Misconfigurations
        misconfigs = result.get("Misconfigurations", [])
        for mis in misconfigs:
            severity = mis.get("Severity", "UNKNOWN").upper()

            if severity == "CRITICAL":
                critical_count += 1
                max_severity = get_higher_severity(max_severity, severity)

            elif severity == "HIGH":
                high_count += 1
                max_severity = get_higher_severity(max_severity, severity)

    return {
        "critical_count": critical_count,
        "high_count": high_count,
        "max_severity": max_severity if (critical_count or high_count) else "LOW"
    }
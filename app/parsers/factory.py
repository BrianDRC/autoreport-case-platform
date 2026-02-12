from .base import BaseScanParser
from .trivy import TrivyScanParser


_PARSERS: dict[str, BaseScanParser] = {
    "trivy": TrivyScanParser(),
    # Futuro:
    # "xray": XrayScanParser(),
    # "wiz": WizScanParser(),
    # "qualys": QualysScanParser(),
}


def get_parser(scan_provider: str) -> BaseScanParser:
    key = (scan_provider or "").strip().lower()
    parser = _PARSERS.get(key)
    if not parser:
        raise ValueError(f"Unsupported scan_provider: {scan_provider}")
    return parser

from fastapi import HTTPException

from app.models import BuildCase, CaseStatus
from app.parsers.factory import get_parser
from app.repositories.case_repository import CaseRepository


class CaseService:
    def __init__(self, repo: CaseRepository):
        self.repo = repo

    @staticmethod
    def build_case_key(meta) -> str:
        if meta.pr_id:
            return f"{meta.provider}::{meta.org}::{meta.repo}::PR::{meta.pr_id}"
        return f"{meta.provider}::{meta.org}::{meta.repo}::BR::{meta.branch}"

    @staticmethod
    def should_gate(meta, critical: int, high: int) -> bool:
        return bool(meta.pr_id and meta.target_branch == "main" and (critical > 0 or high > 0))

    def upsert_from_scan_payload(self, payload):
        meta = payload.metadata
        case_key = self.build_case_key(meta)

        # Select parser
        try:
            parser = get_parser(payload.scan_provider)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        normalized = parser.parse(payload.scan_report)

        critical = normalized.critical_count
        high = normalized.high_count
        max_severity = normalized.max_severity.value

        status = CaseStatus.OPEN if (critical > 0 or high > 0) else CaseStatus.RESOLVED
        gate = self.should_gate(meta, critical, high)

        existing = self.repo.get_by_case_key(case_key)

        if existing:
            existing.scan_provider = payload.scan_provider.lower().strip()
            existing.status = status.value

            existing.critical_vulns = normalized.critical_vulns
            existing.high_vulns = normalized.high_vulns
            existing.critical_misconfig = normalized.critical_misconfig
            existing.high_misconfig = normalized.high_misconfig
            existing.critical_count = critical
            existing.high_count = high
            existing.max_severity = max_severity

            existing.latest_commit_sha = meta.commit_sha
            existing.latest_image_digest = payload.image.digest
            existing.latest_run_id = meta.run_id
            existing.latest_run_url = meta.run_url

            existing.scan_report_json = payload.scan_report

            self.repo.save(existing)
            return status.value, critical, high, max_severity, gate

        case = BuildCase(
            case_key=case_key,
            provider=meta.provider,
            org_name=meta.org,
            repo_name=meta.repo,
            branch_name=meta.branch,
            pr_id=meta.pr_id,
            target_branch=meta.target_branch,

            scan_provider=payload.scan_provider.lower().strip(),
            status=status.value,

            critical_vulns=normalized.critical_vulns,
            high_vulns=normalized.high_vulns,
            critical_misconfig=normalized.critical_misconfig,
            high_misconfig=normalized.high_misconfig,
            critical_count=critical,
            high_count=high,
            max_severity=max_severity,

            latest_commit_sha=meta.commit_sha,
            latest_image_digest=payload.image.digest,
            latest_run_id=meta.run_id,
            latest_run_url=meta.run_url,

            scan_report_json=payload.scan_report,
        )

        self.repo.save(case)
        return status.value, critical, high, max_severity, gate

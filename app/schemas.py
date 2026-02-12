from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


# ==========================
# Ingest v1 (Generic Scan)
# ==========================

class ScanMetadata(BaseModel):
    provider: str  # CI provider, e.g. "github"
    org: str
    repo: str
    branch: str
    pr_id: Optional[int] = None
    target_branch: Optional[str] = None
    commit_sha: str
    run_id: str
    run_url: str


class ImageInfo(BaseModel):
    name: str
    tag: str
    digest: str


class ScanIngestRequest(BaseModel):
    scan_provider: str = Field(..., description="Security scanner provider: trivy/xray/wiz/qualys/etc")
    metadata: ScanMetadata
    image: ImageInfo
    scan_report: Dict[str, Any]


class ScanIngestResponse(BaseModel):
    case_status: str
    critical: int
    high: int
    max_severity: str
    gate: bool


# ==========================
# Cases (Read)
# ==========================

class CaseListResponse(BaseModel):
    id: int
    case_key: str
    provider: str
    org_name: str
    repo_name: str
    branch_name: str
    pr_id: Optional[int]
    target_branch: Optional[str]
    scan_provider: str

    status: str
    critical_vulns: int
    high_vulns: int
    critical_misconfig: int
    high_misconfig: int
    critical_count: int
    high_count: int
    max_severity: str

    latest_commit_sha: str
    latest_image_digest: str
    latest_run_id: str
    latest_run_url: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseReportResponse(BaseModel):
    id: int
    case_key: str
    scan_provider: str
    scan_report: Dict[str, Any]

    class Config:
        from_attributes = True

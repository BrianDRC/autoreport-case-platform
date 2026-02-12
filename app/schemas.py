from pydantic import BaseModel
from typing import Optional, Dict, Any


# ==========================
# Test Ingest (MVP inicial)
# ==========================

class IngestTestRequest(BaseModel):
    case_key: str
    repo: str
    branch: str
    commit: str


class IngestTestResponse(BaseModel):
    status: str


# ==========================
# Trivy Ingest Schemas
# ==========================

class TrivyMetadata(BaseModel):
    provider: str
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


class TrivyIngestRequest(BaseModel):
    metadata: TrivyMetadata
    image: ImageInfo
    trivy_report: Dict[str, Any]


class TrivyIngestResponse(BaseModel):
    case_status: str
    critical: int
    high: int
    gate: bool

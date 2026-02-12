from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import Base, engine, get_db
from .models import BuildCase
from .schemas import (
    IngestTestRequest,
    IngestTestResponse,
    TrivyIngestRequest,
    TrivyIngestResponse,
)
from .settings import API_KEY
from .trivy_parser import parse_trivy_report


app = FastAPI(title="AutoReport Case Platform")


# ==========================
# Auto-create tables (MVP)
# ==========================
Base.metadata.create_all(bind=engine)


# ==========================
# Health
# ==========================
@app.get("/health")
def health():
    return {"status": "ok"}


# ==========================
# Test Endpoint (Legacy MVP)
# ==========================
@app.post("/api/v1/ingest/test", response_model=IngestTestResponse)
def ingest_test(
    payload: IngestTestRequest,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    existing = db.execute(
        select(BuildCase).where(BuildCase.case_key == payload.case_key)
    ).scalar_one_or_none()

    if existing:
        existing.latest_commit_sha = payload.commit
        db.commit()
        return {"status": "updated"}

    case = BuildCase(
        case_key=payload.case_key,
        provider="test",
        org_name="test",
        repo_name=payload.repo,
        branch_name=payload.branch,
        pr_id=None,
        target_branch=None,
        status="OPEN",
        critical_count=0,
        high_count=0,
        max_severity="LOW",
        latest_commit_sha=payload.commit,
        latest_image_digest="test",
        latest_run_id="test",
        latest_run_url="test",
        trivy_report_json={},
    )

    db.add(case)
    db.commit()

    return {"status": "created"}


# ==========================
# Trivy Ingest (Real Logic)
# ==========================
@app.post("/api/v1/ingest/trivy", response_model=TrivyIngestResponse)
def ingest_trivy(
    payload: TrivyIngestRequest,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):

    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    metadata = payload.metadata

    # --------------------------
    # Construcción inteligente case_key
    # --------------------------
    if metadata.pr_id:
        case_key = (
            f"{metadata.provider}::{metadata.org}::{metadata.repo}::PR::{metadata.pr_id}"
        )
    else:
        case_key = (
            f"{metadata.provider}::{metadata.org}::{metadata.repo}::BR::{metadata.branch}"
        )

    # --------------------------
    # Parse Trivy
    # --------------------------
    parsed = parse_trivy_report(payload.trivy_report)

    critical = parsed["critical_count"]
    high = parsed["high_count"]
    max_severity = parsed["max_severity"]

    # --------------------------
    # Determinar status
    # --------------------------
    status = "OPEN" if (critical > 0 or high > 0) else "RESOLVED"

    # --------------------------
    # Gate Logic
    # --------------------------
    gate = False
    if metadata.pr_id and metadata.target_branch == "main":
        if critical > 0 or high > 0:
            gate = True

    # --------------------------
    # Upsert Case
    # --------------------------
    existing = db.execute(
        select(BuildCase).where(BuildCase.case_key == case_key)
    ).scalar_one_or_none()

    if existing:
        existing.status = status
        existing.critical_count = critical
        existing.high_count = high
        existing.max_severity = max_severity
        existing.latest_commit_sha = metadata.commit_sha
        existing.latest_image_digest = payload.image.digest
        existing.latest_run_id = metadata.run_id
        existing.latest_run_url = metadata.run_url
        existing.trivy_report_json = payload.trivy_report
        db.commit()
    else:
        case = BuildCase(
            case_key=case_key,
            provider=metadata.provider,
            org_name=metadata.org,
            repo_name=metadata.repo,
            branch_name=metadata.branch,
            pr_id=metadata.pr_id,
            target_branch=metadata.target_branch,
            status=status,
            critical_count=critical,
            high_count=high,
            max_severity=max_severity,
            latest_commit_sha=metadata.commit_sha,
            latest_image_digest=payload.image.digest,
            latest_run_id=metadata.run_id,
            latest_run_url=metadata.run_url,
            trivy_report_json=payload.trivy_report,
        )
        db.add(case)
        db.commit()

    return {
        "case_status": status,
        "critical": critical,
        "high": high,
        "gate": gate,
    }

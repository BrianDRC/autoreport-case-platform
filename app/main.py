from typing import List

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import Base, engine, get_db
from .models import BuildCase, CaseStatus
from .schemas import (
    IngestTestRequest,
    IngestTestResponse,
    TrivyIngestRequest,
    TrivyIngestResponse,
    CaseListResponse,
)
from .settings import API_KEY
from .trivy_parser import parse_trivy_report


app = FastAPI(title="SecureCase – CI Security Case Engine")


# 🔥 Crear tablas en startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# ==========================
# Health
# ==========================
@app.get("/health")
def health():
    return {"status": "ok"}


# ==========================
# Trivy Ingest
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

    # Construcción case_key
    if metadata.pr_id:
        case_key = (
            f"{metadata.provider}::{metadata.org}::{metadata.repo}::PR::{metadata.pr_id}"
        )
    else:
        case_key = (
            f"{metadata.provider}::{metadata.org}::{metadata.repo}::BR::{metadata.branch}"
        )

    parsed = parse_trivy_report(payload.trivy_report)

    critical = parsed["critical_count"]
    high = parsed["high_count"]
    max_severity = parsed["max_severity"]

    status = (
        CaseStatus.OPEN
        if (critical > 0 or high > 0)
        else CaseStatus.RESOLVED
    )

    gate = False
    if metadata.pr_id and metadata.target_branch == "main":
        if critical > 0 or high > 0:
            gate = True

    existing = db.execute(
        select(BuildCase).where(BuildCase.case_key == case_key)
    ).scalar_one_or_none()

    if existing:
        existing.status = status.value
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
            status=status.value,
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
        "case_status": status.value,
        "critical": critical,
        "high": high,
        "gate": gate,
    }


# ==========================
# List Cases
# ==========================
@app.get("/api/v1/cases", response_model=List[CaseListResponse])
def list_cases(
    repo: str | None = Query(None),
    branch: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(BuildCase)

    if repo:
        query = query.filter(BuildCase.repo_name == repo)

    if branch:
        query = query.filter(BuildCase.branch_name == branch)

    if status:
        query = query.filter(BuildCase.status == status)

    return query.order_by(BuildCase.created_at.desc()).all()


@app.get("/api/v1/cases/{case_id}", response_model=CaseListResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(BuildCase).filter(BuildCase.id == case_id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return case

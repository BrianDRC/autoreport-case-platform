from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ScanIngestRequest, ScanIngestResponse
from app.settings import API_KEY
from app.repositories.case_repository import CaseRepository
from app.services.case_service import CaseService

router = APIRouter(prefix="/api/v1", tags=["ingest"])


def authorize(x_api_key: str | None):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/ingest/scan", response_model=ScanIngestResponse)
def ingest_scan(
    payload: ScanIngestRequest,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    authorize(x_api_key)

    service = CaseService(CaseRepository(db))
    status, critical, high, max_sev, gate = service.upsert_from_scan_payload(payload)

    return {
        "case_status": status,
        "critical": critical,
        "high": high,
        "max_severity": max_sev,
        "gate": gate,
    }

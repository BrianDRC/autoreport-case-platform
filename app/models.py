from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from .db import Base


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class Severity(str, Enum):
    NONE = "NONE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BuildCase(Base):
    __tablename__ = "build_cases"

    __table_args__ = (
        Index("ix_case_key", "case_key"),
        Index("ix_repo_branch", "repo_name", "branch_name"),
        Index("ix_scan_provider", "scan_provider"),
        Index("ix_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Un identificador estable por PR o branch (para actualizar con commits)
    case_key: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)

    # CI provider / repo metadata
    provider: Mapped[str] = mapped_column(String(50), nullable=False)      # e.g. "github"
    org_name: Mapped[str] = mapped_column(String(200), nullable=False)
    repo_name: Mapped[str] = mapped_column(String(200), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(200), nullable=False)
    pr_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_branch: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Scanner/provider de seguridad
    scan_provider: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "trivy" / "xray" / "wiz" / "qualys"

    # Estado del case
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    # Conteos normalizados (solo HIGH/CRITICAL, separados por tipo)
    critical_vulns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_vulns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_misconfig: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_misconfig: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Totales para queries rápidas
    critical_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_severity: Mapped[str] = mapped_column(String(20), nullable=False, default=Severity.NONE.value)

    # “Último build” (evidencia)
    latest_commit_sha: Mapped[str] = mapped_column(String(80), nullable=False)
    latest_image_digest: Mapped[str] = mapped_column(String(200), nullable=False)
    latest_run_id: Mapped[str] = mapped_column(String(200), nullable=False)
    latest_run_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Raw report (JSONB) del scanner (Trivy/Xray/Wiz/Qualys...)
    scan_report_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

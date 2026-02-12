from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from .db import Base


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class BuildCase(Base):
    __tablename__ = "build_cases"

    __table_args__ = (
        Index("ix_case_key", "case_key"),
        Index("ix_repo_branch", "repo_name", "branch_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    case_key: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    org_name: Mapped[str] = mapped_column(String(200), nullable=False)
    repo_name: Mapped[str] = mapped_column(String(200), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(200), nullable=False)

    pr_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_branch: Mapped[str | None] = mapped_column(String(200), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    critical_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_severity: Mapped[str] = mapped_column(String(20), nullable=False)

    latest_commit_sha: Mapped[str] = mapped_column(String(80), nullable=False)
    latest_image_digest: Mapped[str] = mapped_column(String(200), nullable=False)
    latest_run_id: Mapped[str] = mapped_column(String(200), nullable=False)
    latest_run_url: Mapped[str] = mapped_column(String(500), nullable=False)

    trivy_report_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

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

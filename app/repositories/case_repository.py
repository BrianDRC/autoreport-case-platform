from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import BuildCase


class CaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_case_key(self, case_key: str) -> BuildCase | None:
        return self.db.execute(
            select(BuildCase).where(BuildCase.case_key == case_key)
        ).scalar_one_or_none()

    def get_by_id(self, case_id: int) -> BuildCase | None:
        return self.db.query(BuildCase).filter(BuildCase.id == case_id).first()

    def list_cases(
        self,
        repo: str | None = None,
        branch: str | None = None,
        status: str | None = None,
        scan_provider: str | None = None,
    ):
        query = self.db.query(BuildCase)
        if repo:
            query = query.filter(BuildCase.repo_name == repo)
        if branch:
            query = query.filter(BuildCase.branch_name == branch)
        if status:
            query = query.filter(BuildCase.status == status)
        if scan_provider:
            query = query.filter(BuildCase.scan_provider == scan_provider)

        return query.order_by(BuildCase.created_at.desc()).all()

    def save(self, entity: BuildCase):
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

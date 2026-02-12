from fastapi import FastAPI
from app.db import Base, engine
from app.api.routes.ingest import router as ingest_router
from app.api.routes.cases import router as cases_router

app = FastAPI(...)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(ingest_router)
app.include_router(cases_router)

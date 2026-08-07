from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import candidates, health, jobs, resumes, screenings
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.db.database import Base, engine
from app.db import models  # noqa: F401

configure_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Resume Screening & Candidate Ranking System",
    version="1.0.0",
    description="An AI-powered system for parsing resumes, extracting job requirements, "
    "and producing explainable candidate rankings.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins] if settings.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(health.router, prefix="/api")
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(screenings.router)

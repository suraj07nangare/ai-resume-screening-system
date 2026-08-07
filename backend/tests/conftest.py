import os
import tempfile
import uuid

os.environ["LLM_PROVIDER"] = "mock"

_TMP_DB_FD, _TMP_DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_TMP_DB_FD)
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB_PATH}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.database import Base
from app.db import models  # noqa: F401
from app.main import app
from app.api.dependencies import get_session

TEST_ENGINE = create_engine(
    f"sqlite:///{_TMP_DB_PATH}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


def _override_get_db():
    db: Session = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = _override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


SAMPLE_RESUME_TEXT = """John Doe
john.doe@example.com
9876543210

Summary
Backend engineer with 3 years of experience building APIs with Python and FastAPI.

Skills
Python, FastAPI, SQL, PostgreSQL, Docker, Git

Experience
Backend Engineer at Acme Corp
3 years building REST APIs and microservices.

Education
Bachelor of Engineering, Computer Science
"""

SAMPLE_JD_TEXT = """We are looking for a Backend Engineer with strong Python and FastAPI skills.
Required: Python, FastAPI, SQL, Docker
Preferred: AWS, Kubernetes
Minimum experience: 2 years
Education: Bachelor degree in Computer Science or related field
"""

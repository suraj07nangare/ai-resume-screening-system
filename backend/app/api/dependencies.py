from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import get_db

DbSession = Session


def get_session() -> Generator[Session, None, None]:
    yield from get_db()

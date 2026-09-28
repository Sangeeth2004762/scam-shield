"""
Scam Shield - Database Module
Initializes SQLite database via SQLModel and provides session dependency.
"""

from __future__ import annotations
import os
from typing import Generator
from sqlmodel import SQLModel, Session, create_engine

# SQLite database file stored in backend/scam_shield.db
DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(DATABASE_DIR, "scam_shield.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_FILE}")

# connect_args={"check_same_thread": False} is required for SQLite with FastAPI multi-threading
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)


def init_db() -> None:
    """Creates database tables if they do not already exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency provider yielding a database session."""
    with Session(engine) as session:
        yield session

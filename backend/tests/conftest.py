import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Problem

# In-memory SQLite database for tests — isolated and fast.
# StaticPool ensures all connections share the same in-memory database.
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database schema for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """A FastAPI TestClient that uses the in-memory test database."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_problem(db_session):
    """Insert and return a sample Parking Lot problem."""
    problem = Problem(
        title="Design a Parking Lot",
        slug="parking-lot",
        difficulty="medium",
        short_description="A parking lot system.",
        description="Design a parking lot for a multi-floor building.",
        requirements="Support vehicle types: motorcycle, car, truck.\nEach floor has spots of different sizes.",
        hints="Think about a Vehicle hierarchy.",
        evaluation_criteria="Clear separation of responsibilities.\nProper abstraction for spot assignment.",
    )
    db_session.add(problem)
    db_session.commit()
    db_session.refresh(problem)
    return problem

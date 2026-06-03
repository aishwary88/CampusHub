"""
Pytest configuration and shared fixtures for the CampusHub backend test suite.

All tests use an in-memory SQLite database so they remain isolated from any
real PostgreSQL instance and can run without network access.
"""

import pytest
from hypothesis import settings as hypothesis_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import Base, get_db
from app.models.user import User, UserRole
from app.auth.password import hash_password

# ---------------------------------------------------------------------------
# Hypothesis profile
# ---------------------------------------------------------------------------

hypothesis_settings.register_profile("default", max_examples=100)
hypothesis_settings.load_profile("default")

# ---------------------------------------------------------------------------
# In-memory SQLite engine / session factory
#
# StaticPool forces SQLAlchemy to reuse a single underlying connection for all
# sessions, which is required for in-memory SQLite: without it every new
# connection sees a fresh (empty) database and tables created by one session
# are invisible to another.
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def db():
    """
    Provide an isolated in-memory SQLite session for each test function.

    Tables are created fresh before each test and dropped afterwards so that
    tests are fully independent and cannot share state.
    """
    # Import all models so SQLAlchemy registers them with Base.metadata
    import app.models.user  # noqa: F401
    import app.models.post  # noqa: F401
    import app.models.club  # noqa: F401
    import app.models.event  # noqa: F401
    import app.models.notification  # noqa: F401

    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Provide a FastAPI TestClient whose ``get_db`` dependency is overridden
    to use the in-memory SQLite session provided by the ``db`` fixture.
    """

    def _override_get_db():
        try:
            yield db
        finally:
            pass  # session lifecycle is managed by the `db` fixture

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Clean up the override after the test so other tests are not affected
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def test_user(db):
    """
    Create and return a pre-verified STUDENT user in the test database.

    Credentials:
        email:    student@mitsgwl.ac.in
        password: testpass123
        role:     STUDENT
    """
    user = User(
        name="Test Student",
        email="student@mitsgwl.ac.in",
        password_hash=hash_password("testpass123"),
        role=UserRole.STUDENT.value,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

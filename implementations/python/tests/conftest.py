"""
Pytest configuration and fixtures for OneRoster Gradebook Service tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.config.database import get_db
from src.main import app
from src.models.models import Category, LineItem, Result, ScoreStatusEnum, StatusEnum

# Test database URL (use a separate test database)
TEST_DATABASE_URL = "postgresql://oneroster_user:oneroster_pass@db:5432/oneroster_gradebook"

# Create test engine
engine = create_engine(TEST_DATABASE_URL, isolation_level="READ COMMITTED")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test with transaction rollback.
    Uses SAVEPOINT for nested transactions to ensure proper cleanup.
    """
    # Create a connection
    connection = engine.connect()
    # Begin a transaction
    transaction = connection.begin()
    # Create a session bound to the connection
    session = TestingSessionLocal(bind=connection)

    # Clean up test data at the start
    try:
        session.execute(text("DELETE FROM results WHERE sourced_id LIKE 'test-%'"))
        session.execute(text("DELETE FROM line_items WHERE sourced_id LIKE 'test-%'"))
        session.execute(text("DELETE FROM categories WHERE sourced_id LIKE 'test-%'"))
        # Skip oauth_tokens cleanup if table doesn't exist (it's managed in auth.py)
        session.commit()
    except Exception:
        session.rollback()
        # Ignore cleanup errors for optional tables
        pass

    try:
        yield session
    finally:
        # Close session
        session.close()
        # Rollback transaction to undo any changes
        transaction.rollback()
        # Close connection
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def oauth_token(client):
    """Get OAuth access token for testing."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly "
            "https://purl.imsglobal.org/spec/or/v1p2/scope/results.readonly "
            "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput "
            "https://purl.imsglobal.org/spec/or/v1p2/scope/results.delete",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def sample_category(db_session):
    """Create a sample category for testing."""
    # Use unique ID for each test run to avoid conflicts
    import time

    category_id = f"test-cat-{int(time.time() * 1000000)}"
    category = Category(
        sourced_id=category_id,
        status=StatusEnum.active,
        title="Test Category",
        weight=0.5,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_line_item(db_session, sample_category):
    """Create a sample line item for testing."""
    import time

    line_item_id = f"test-li-{int(time.time() * 1000000)}"
    line_item = LineItem(
        sourced_id=line_item_id,
        status=StatusEnum.active,
        title="Test Assignment",
        description="Test assignment description",
        class_sourced_id="class-001",
        category_sourced_id=sample_category.sourced_id,
        result_value_min=0.0,
        result_value_max=100.0,
    )
    db_session.add(line_item)
    db_session.commit()
    db_session.refresh(line_item)
    return line_item


@pytest.fixture
def sample_result(db_session, sample_line_item):
    """Create a sample result for testing."""
    import time

    result_id = f"test-res-{int(time.time() * 1000000)}"
    result = Result(
        sourced_id=result_id,
        status=StatusEnum.active,
        line_item_sourced_id=sample_line_item.sourced_id,
        student_sourced_id="student-001",
        score_status=ScoreStatusEnum.earnedFull,
        score=85.5,
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(result)
    return result
